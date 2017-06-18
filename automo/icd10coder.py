"""
ICD-10 Coder
"""
import wx
import wx.html
from sqlalchemy import or_, and_
from urlparse import urlparse, parse_qs
from ObjectListView import ObjectListView, ColumnDefn, OLVEvent

from objectlistviewmod import ObjectListViewMod
from database import Icd10Class


class SearchResultList(wx.HtmlListBox):
    """
    Display results of sqlalchemy query
    """
    def __init__(self, parent, session, style=wx.SUNKEN_BORDER, **kwds):
        super(SearchResultList, self).__init__(
            parent, style=style, **kwds
        )
        self.parent = parent
        self.session = session
        self.query_string = ""
        self.query_result = None
        self.SetItemCount(0)

        self.visible_begin = -1
        self.visible_end = -1
        self.visible_items = []

        if wx.Platform == "__WXMSW__":
            self.SetSelectionBackground(wx.SystemSettings_GetColour(wx.SYS_COLOUR_MENUHILIGHT))
        else:
            self.SetSelectionBackground(wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT))


    def clear(self):
        """Remove all items from list"""
        self.SetItemCount(0)
        self.query_string = ""
        self.query_result = None
        self.Refresh()


    def set_result(self, query_result, query_string):
        """
        Set the sqlalchemy query result, and highlight the 
        query string in the results.
        """
        self.query_string = query_string
        self.query_result = query_result

        self.visible_begin = -1
        self.visible_end = -1
        self.visible_items = []

        self.ScrollToRow(0)
        self.SetItemCount(self.query_result.count())

        self.RefreshRows(self.GetVisibleRowsBegin(), self.GetVisibleRowsEnd())
        self.Refresh()


    def GetSelectedObject(self):
        """Return the selected Object"""
        index = self.GetSelection() - self.GetVisibleRowsBegin()
        try:
            return self.visible_items[index]
        except IndexError:
            return None


    def _fetch_visible(self):
        self.visible_begin = self.GetVisibleRowsBegin()
        self.visible_end = self.GetVisibleRowsEnd()
        row_limit = self.visible_end - self.visible_begin
        if row_limit < 50:
            row_limit = 50
        self.visible_items = self.query_result\
                                .offset(self.visible_begin)\
                                .limit(row_limit).all()


    def _htmlformat(self, text, substring):
        """
        Format the text
        to highlight the substring in html
        """
        # empty substring
        if len(substring) == 0:
            return text
        else:
            return text.replace(substring, '<b>' + substring + '</b>', 1)


    def OnGetItem(self, n):
        if self.query_result is None:
            return ""
        start = self.GetVisibleRowsBegin()
        end = self.GetVisibleRowsEnd()
        if not(start == self.visible_begin and end == self.visible_end):
            self._fetch_visible()

        try:
            item = self.visible_items[n - self.visible_begin]
            return self._htmlformat(
                u"{0} {1}".format(item.code, item.preferred_plain), self.query_string)
        except IndexError:
            return "Click to load..."




class Icd10ChapterTree(wx.TreeCtrl):
    """
    Tree of Icd10 Chapters and blocks. Nodes expand lazily only when they are clicked.
    """
    def __init__(self, parent, session, **kwds):
        super(Icd10ChapterTree, self).__init__(
            parent, style=wx.TR_HAS_BUTTONS|wx.wx.TR_HAS_VARIABLE_ROW_HEIGHT|wx.SUNKEN_BORDER,
            **kwds
        )

        self.session = session

        wx.EVT_TREE_ITEM_EXPANDING(self, self.GetId(), self._on_expand)

        self._build_tree()


    def set_class(self, icd10_class):
        """Set Selected Icd10 Class and display it"""
        def get_class_crumbs(iclass):
            """Get path to chapter"""
            result = [iclass.code]
            if iclass.parent is not None:
                result.extend(get_class_crumbs(iclass.parent))
            return result

        crumbs = get_class_crumbs(icd10_class)
        print crumbs

        current_parent_id = self.root_id
        current_item_id, cookie = self.GetFirstChild(current_parent_id)
        for crumb_code in reversed(crumbs):
            while current_item_id.IsOk():
                item_class, status = self.GetPyData(current_item_id)
                if item_class.code == crumb_code:
                    if crumb_code == crumbs[0]:
                        self.SelectItem(current_item_id)
                        break
                    else:
                        if status is False:
                            self.DeleteChildren(current_item_id)
                            self.SetPyData(current_item_id, (item_class, True))
                            self._extend_tree(current_item_id)
                        self.Expand(current_item_id)
                        current_parent_id = current_item_id
                        current_item_id, cookie = self.GetFirstChild(current_parent_id)
                        break
                else:
                    current_item_id, cookie = self.GetNextChild(current_parent_id, cookie)


    def GetSelectedObject(self):
        """Return the selected object"""
        item_id = self.GetSelection()
        if not item_id.IsOk():
            return None

        item_class = self.GetPyData(item_id)[0]
        return item_class


    def _build_tree(self):
        self.root_id = self.AddRoot("ICD-10")
        self.SetPyData(self.root_id, (None, True))
        self._extend_tree(self.root_id)
        self.Expand(self.root_id)


    def _extend_tree(self, parent_id):
        parent_class = self.GetPyData(parent_id)[0]

        if parent_class is None:
            parent_code = None
        else:
            parent_code = parent_class.code

        child_classes = self.session.query(Icd10Class).\
                            filter(Icd10Class.parent_code == parent_code).all()

        for child in child_classes:
            child_title = "{0} {1}".format(child.code, child.preferred_plain)
            child_id = self.AppendItem(parent_id, child_title)
            self.SetPyData(child_id, (child, False))

            grand_child_class_count = self.session.query(Icd10Class)\
                                        .filter(Icd10Class.parent_code == child.code).count()

            if grand_child_class_count > 0:
                self.AppendItem(child_id, "Loading...")


    def _on_expand(self, event):
        expanded_id = event.GetItem()
        if not expanded_id.IsOk():
            expanded_id = self.GetSelection()

        expanded_class, status = self.GetPyData(expanded_id)
        if status is False:
            self.DeleteChildren(expanded_id)
            self._extend_tree(expanded_id)
            self.SetPyData(expanded_id, (expanded_class, True))


class Icd10CategoryList(wx.SimpleHtmlListBox):
    """
    List of Icd10 Categories in a block
    """
    def __init__(self, parent, session, **kwds):
        super(Icd10CategoryList, self).__init__(parent, **kwds)

        self.session = session

        self.selected_category = None
        self.categories = []

        if wx.Platform == "__WXMSW__":
            self.SetSelectionBackground(wx.SystemSettings_GetColour(wx.SYS_COLOUR_MENUHILIGHT))
        else:
            self.SetSelectionBackground(wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT))


    def _goto_selected(self):
        list_index = 0
        for category in self.categories:
            if category.code == self.selected_category.code:
                self.SetSelection(list_index)
            list_index += 1


    def set_code(self, code):
        """Set the category that is selected, search by code"""
        self.selected_category = self.session.query(Icd10Class)\
                                    .filter(Icd10Class.code == code)\
                                    .one()
        self.set_block(self.selected_category.parent_block_code)
        self._goto_selected()


    def set_category(self, category):
        """Set the category that is selected"""
        if self.selected_category is not None:
            if category.code == self.selected_category.code:
                return

            if category.parent_block_code == self.selected_category.parent_block_code:
                self.selected_category = category
                self._goto_selected()
                return

        self.selected_category = category
        self.set_block(self.selected_category.parent_block_code)
        self._goto_selected()


    def set_block(self, block_code):
        """Set the currently displayed block"""
        self.categories = []
        self.Clear()
        categories = self.session.query(Icd10Class)\
                        .filter(
                            and_(
                                Icd10Class.kind == "category",
                                Icd10Class.parent_block_code == block_code
                            )
                        )

        htmls = []
        for category in categories:
            self.categories.append(category)
            html = u'<table width="100%" cellspacing="0" border="0"><tr><td width="50"><b>{0}</b></td>'\
                    u'<td><b>{1}</b></td></tr><tr><td></td><td>{2}</td></tr></table>'
            if len(category.code) <= 3:
                html = u'<table width="100%" cellspacing="0" border="0"><tr height="2" bgcolor="black"><td cellpadding="0" colspan="2"></td></tr><tr><td width="50" bgcolor="black"><font color="white"><b>{0}</b></font></td>'\
                    u'<td><b>{1}</b></td></tr><tr><td></td><td>{2}</td></tr></table>'

            content = ""

            if category.preferred_long is not None:
                content += u"{0}".format(category.preferred_long)

            if category.text is not None:
                content += u"{0}".format(category.text)

            if category.inclusion is not None:
                content += u'<table width="100%"><tr><td valign="top" width="40"><b><i>Incl.:</i></b></td><td>{0}</td><tr></table>'.format(category.inclusion)

            if category.exclusion is not None:
                content += u'<table width="100%"><tr><td valign="top" width="40"><b><i>Excl.:</i></b></td><td>{0}</td><tr></table>'.format(category.exclusion)

            if category.note is not None:
                content += u'<table width="100%"><tr><td valign="top" width="40"><b><i>Note:</i></b></td><td>{0}</td><tr></table>'.format(category.note)

            if category.coding_hint is not None:
                content += u'<div><b><i>Coding Hint:</i></b> {0}</div>'.format(category.coding_hint)

            html = html.format(category.code, category.preferred, content)

            htmls.append(html)

        self.AppendItems(htmls)


class Icd10Coder(wx.Dialog):
    """
    Dialog to search for and select ICD-10 Category codes
    """
    def __init__(self, parent, session, size=wx.Size(1000, 600), **kwds):
        super(Icd10Coder, self).__init__(
            parent, style=wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION,
            size=size, **kwds)

        self.session = session

        grid_sizer = wx.GridBagSizer(0, 0)

        #Search terms entered here
        self.txt_search = wx.TextCtrl(self)
        self.txt_search.Bind(wx.EVT_TEXT, self._on_change_filter)
        grid_sizer.Add(self.txt_search, wx.GBPosition(0, 0),
                       flag=wx.EXPAND | wx.ALL, border=5)

        #Displays search results
        self.result_list = SearchResultList(self, self.session, size=(200, -1))
        self.result_list.Bind(wx.EVT_LISTBOX, self._on_result_selected)
        grid_sizer.Add(self.result_list, wx.GBPosition(1, 0),
                       flag=wx.EXPAND | wx.ALL, border=5)

        #Tree view of icd-10 chapters and blocks
        self.chapter_tree = Icd10ChapterTree(self, self.session, size=wx.Size(200, 0))
        self.chapter_tree.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_tree_selected)
        grid_sizer.Add(self.chapter_tree, wx.GBPosition(0, 1), wx.GBSpan(2, 1),
                       flag=wx.EXPAND | wx.ALL, border=5)

        #List of selected categories
        self.category_list = Icd10CategoryList(self, session)
        self.category_list.Bind(wx.html.EVT_HTML_LINK_CLICKED, self._on_link_category_list)
        grid_sizer.Add(self.category_list, wx.GBPosition(0, 2), wx.GBSpan(2, 1),
                       flag=wx.EXPAND | wx.ALL, border=5)

        self.status = wx.StatusBar(self)
        grid_sizer.Add(self.status, wx.GBPosition(2, 0), wx.GBSpan(1, 3),
                       flag=wx.EXPAND, border=0)

        grid_sizer.AddGrowableCol(2)
        grid_sizer.AddGrowableRow(1)
        self.SetSizer(grid_sizer)


    def _on_change_filter(self, event):
        """ search and display results """
        items = self.session.query(Icd10Class)

        str_search = self.txt_search.GetValue()
        if str_search != "":
            items = items.filter(Icd10Class.kind == "category").filter(
                or_(
                    Icd10Class.code.like("%{0}%".format(str_search)),
                    Icd10Class.preferred_plain.like("%{0}%".format(str_search))
                )
            )

            self.result_list.set_result(items, str_search)
        else:
            self.result_list.clear()


    def _on_result_selected(self, event):
        result_selected = self.result_list.GetSelectedObject()
        #self.category_list.set_category(result_selected)
        self.chapter_tree.set_class(result_selected)
        print "Search result selected..."


    def _on_tree_selected(self, event):
        print "Tree Selected"
        tree_selected = self.chapter_tree.GetSelectedObject()
        self.category_list.set_category(tree_selected)


    def _on_link_category_list(self, event):
        link_info = event.GetLinkInfo()
        href_p = urlparse(link_info.GetHref())
        if href_p.path == "category":
            query_p = parse_qs(href_p.query)
            if "code" in query_p.keys():
                self.category_list.set_code(query_p['code'][0])
        print "Clicked a link href={0}".format(link_info.GetHref())


def main():
    import database
    database.StartEngine("sqlite:///wardpresc-data.db", False, "")
    session = database. Session()

    app = wx.PySimpleApp(0)

    dlg = Icd10Coder(None, session)
    app.SetTopWindow(dlg)
    dlg.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
