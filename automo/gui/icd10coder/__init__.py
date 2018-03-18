"""ICD-10 Coder"""
import string
import datetime
import re
from urlparse import urlparse, parse_qs
import wx
import wx.html
from sqlalchemy import or_, and_
from sqlalchemy.orm.exc import NoResultFound

from ... import database as db
from ..widgets import DbQueryResultBox, DbComboBox, PyDatePickerCtrl
from .icd10chaptertree import Icd10ChapterTree
from .icd10categorylist import Icd10CategoryList


class Icd10Coder(wx.Dialog):
    """Dialog to search for and select ICD-10 Category codes"""
    def __init__(self, parent, session, size=wx.Size(1000, 600), **kwds):
        super(Icd10Coder, self).__init__(
            parent, style=wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION,
            size=size, **kwds)

        self.SetTitle("ICD-10")

        self.session = session

        #self.problem = None
        #self.selected_category = None
        self.selected_icd10class = None
        self.selected_start_time = None
        self.selected_comment = None
        self.selected_modifier_class = None
        self.selected_modifier_extra_class = None

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        #right panel with tabs
        self.left_panel = wx.Notebook(splitter)
        self.left_panel.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_change_left_panel)

        #search panel
        search_panel = wx.Panel(self.left_panel)
        search_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.txt_search = wx.TextCtrl(search_panel)
        self.txt_search.Bind(wx.EVT_TEXT, self._on_change_filter)
        search_panel_sizer.Add(self.txt_search, 0,
                               flag=wx.EXPAND | wx.ALL, border=5)

        self.result_list = DbQueryResultBox(search_panel,
                                            self._search_result_decorator,
                                            size=(200, -1))
        self.result_list.Bind(wx.EVT_LISTBOX, self._on_result_selected)
        search_panel_sizer.Add(self.result_list, 1,
                               flag=wx.EXPAND | wx.ALL, border=5)

        search_panel.SetSizer(search_panel_sizer)
        self.left_panel.AddPage(search_panel, "Search")

        #browse panel
        browse_panel = wx.Panel(self.left_panel)
        browse_panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.chapter_tree = Icd10ChapterTree(browse_panel, self.session, size=wx.Size(200, 0))
        self.chapter_tree.Bind(wx.EVT_TREE_SEL_CHANGED, self._on_tree_selected)
        browse_panel_sizer.Add(self.chapter_tree, 1,
                               flag=wx.EXPAND | wx.ALL, border=5)
        browse_panel.SetSizer(browse_panel_sizer)
        self.left_panel.AddPage(browse_panel, "Browse")

        #List of selected categories
        self.right_panel = wx.Panel(splitter)
        right_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.browser_title = wx.html.HtmlWindow(
            self.right_panel, style=wx.html.HW_SCROLLBAR_AUTO | wx.html.HW_NO_SELECTION | wx.BORDER_THEME,
            size=(-1, 75))
        right_panel_sizer.Add(self.browser_title, 0,
                              flag=wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        self.browser_title.SetPage(
            "<table><tr><td><b>Internation Classification of Disease - 10</b></td></tr></table>")

        self.category_list = Icd10CategoryList(self.right_panel, session)
        self.category_list.Bind(wx.EVT_LISTBOX, self._on_change_category)
        self.category_list.Bind(wx.html.EVT_HTML_LINK_CLICKED, self._on_link_category_list)
        right_panel_sizer.Add(self.category_list, 1,
                              flag=wx.EXPAND | wx.RIGHT | wx.LEFT | wx.BOTTOM, border=5)

        self.right_panel.SetSizer(right_panel_sizer)

        splitter.SplitVertically(self.left_panel, self.right_panel)
        splitter.SetSashPosition(250)
        sizer.Add(splitter, 1, wx.EXPAND)

        foot_sizer = wx.BoxSizer(wx.VERTICAL)
        foot_sizer.AddSpacer(75)

        self.lbl_modifier = wx.StaticText(self, label="Modifier")
        self.lbl_modifier.Hide()
        foot_sizer.Add(self.lbl_modifier, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx. LEFT, border=5)
        self.cmb_modifier = DbComboBox(self, self._modifier_decorator, size=(200, -1))
        self.cmb_modifier.Hide()
        foot_sizer.Add(self.cmb_modifier, 0,
                       wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx. LEFT, border=5)

        self.lbl_modifier_extra = wx.StaticText(self, label="Additional Modifier")
        self.lbl_modifier_extra.Hide()
        foot_sizer.Add(self.lbl_modifier_extra, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx. LEFT,
                       border=5)
        self.cmb_modifier_extra = DbComboBox(self, self._modifier_decorator, size=(200, -1))
        self.cmb_modifier_extra.Hide()
        foot_sizer.Add(self.cmb_modifier_extra, 0,
                       wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx. LEFT, border=5)

        self.lbl_date = wx.StaticText(self, label="Date")
        foot_sizer.Add(self.lbl_date, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx. LEFT,
                       border=5)
        self.date_picker = PyDatePickerCtrl(self, style=wx.adv.DP_DROPDOWN)
        foot_sizer.Add(self.date_picker, 0,
                       wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx. LEFT, border=5)

        self.lbl_comment = wx.StaticText(self, label="Comment")
        foot_sizer.Add(self.lbl_comment, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx. LEFT,
                       border=5)
        self.txt_comment = wx.TextCtrl(self, size=(200, 60),
                                       style=wx.TE_MULTILINE)
        foot_sizer.Add(self.txt_comment, 0,
                       wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx. LEFT, border=5)

        foot_sizer.AddStretchSpacer()

        button_sizer = wx.BoxSizer(wx.VERTICAL)
        self.chk_favourites = wx.CheckBox(self, label="Add to Favourites")
        button_sizer.Add(self.chk_favourites, 0, wx.EXPAND | wx.ALL, border=5)
        self.btn_ok = wx.Button(self, label="OK")
        self.btn_ok.Bind(wx.EVT_BUTTON, self._on_ok)
        button_sizer.Add(self.btn_ok, 0, wx.EXPAND | wx.ALL, border=5)
        self.btn_cancel = wx.Button(self, label="Cancel")
        self.btn_cancel.Bind(wx.EVT_BUTTON, self._on_cancel)
        button_sizer.Add(self.btn_cancel, 0, wx.EXPAND | wx.ALL, border=5)
        foot_sizer.Add(button_sizer, 0, wx.EXPAND | wx.ALL, border=5)

        sizer.Add(foot_sizer, 0, wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(sizer)

        self.Layout()


    def ShowModal(self, icd10class=None, start_time=None, comment=None, modifier_class=None, modifier_extra_class=None):
        self.selected_icd10class = icd10class
        self.selected_start_time = start_time
        self.selected_comment = comment
        self.selected_modifier_class = modifier_class
        self.selected_modifier_extra_class = modifier_extra_class

        self.txt_search.SetValue("")

        update_tree = False
        if self.selected_icd10class is None:
            selection = self.chapter_tree.GetSelection()
            if selection.IsOk():
                self.chapter_tree.SelectItem(selection, False)
            self.category_list.set_category(None)
            self.left_panel.SetSelection(0)
        else:
            update_tree = True
            self.chapter_tree.initialize()
            self.left_panel.SetSelection(1)

        self.set_category(self.selected_icd10class, update_tree=update_tree)

        if self.selected_start_time is None:
            self.selected_start_time = datetime.datetime.now()

        self.date_picker.set_pydatetime(self.selected_start_time)

        if self.selected_comment is not None:
            self.txt_comment.ChangeValue(self.selected_comment)
        
        if modifier_class is not None:
            self.cmb_modifier.set_selected_item(modifier_class)

        if modifier_extra_class is not None:
            self.cmb_modifier_extra.set_selected_item(modifier_extra_class)

        return super(Icd10Coder, self).ShowModal()


    def set_category(self, icd10class, update_tree=False):
        """Set currently displayed db.Icd10Class"""

        if icd10class is None:
            self.category_list.set_category(None)
            self._update_browser_title(icd10class)
            return

        self.category_list.set_category(icd10class)
        self._update_browser_title(icd10class)

        if update_tree:
            active_page_text = self.left_panel.GetPageText(self.left_panel.GetSelection())
            if active_page_text == "Browse":
                self.chapter_tree.set_class(icd10class)

        if icd10class.modifier is not None:
            self.lbl_modifier.Show()
            self.lbl_modifier.SetLabel(
                icd10class.modifier.name)
            self.cmb_modifier.Show()
            self.cmb_modifier.set_items(
                icd10class.modifier.classes)
            if self.selected_modifier_class is not None:
                if self.selected_modifier_class.modifier.code == icd10class.modifier_code:
                    self.cmb_modifier.set_selected_item(self.selected_modifier_class)
                else:
                    self.selected_modifier_class = None
        else:
            self.lbl_modifier.Hide()
            self.cmb_modifier.Hide()
            self.cmb_modifier.clear()
            self.selected_modifier_class = None

        if icd10class.modifier_extra is not None:
            self.lbl_modifier_extra.Show()
            self.lbl_modifier_extra.SetLabel(
                icd10class.modifier_extra.name)
            self.cmb_modifier_extra.Show()
            self.cmb_modifier_extra.set_items(
                icd10class.modifier_extra.classes)
            if self.selected_modifier_extra_class is not None:
                if self.selected_modifier_extra_class.modifier.code == icd10class.modifier_extra_code:
                    self.cmb_modifier.set_selected_item(self.selected_modifier_extra_class)
                else:
                    self.selected_modifier_extra_class = None
        else:
            self.lbl_modifier_extra.Hide()
            self.cmb_modifier_extra.Hide()
            self.cmb_modifier_extra.clear()
            self.selected_modifier_extra_class = None

        self.Layout()


    def get_problem(self):
        new_problem = db.Problem()
        new_problem.icd10class = self.category_list.get_selected_category()
        new_problem.icd10modifier_class = self.cmb_modifier.get_selected_item()
        new_problem.icd10modifier_extra_class = self.cmb_modifier_extra.get_selected_item()
        new_problem.comment = self.txt_comment.GetValue()
        new_problem.start_time = self.date_picker.get_pydatetime()
        if new_problem.comment == "":
            new_problem.comment = None
        return new_problem


    def update_problem(self, problem):
        problem.icd10class = self.category_list.get_selected_category()
        problem.icd10modifier_class = self.cmb_modifier.get_selected_item()
        problem.icd10modifier_extra_class = self.cmb_modifier_extra.get_selected_item()
        problem.comment = self.txt_comment.GetValue()
        problem.start_time = self.date_picker.get_pydatetime()
        if problem.comment == "":
            problem.comment = None


    def _on_ok(self, event):
        if self.category_list.get_selected_category() is None:
            print("TODO: Error message nothing selected")
            self.EndModal(wx.ID_CANCEL)
            return

        if self.chk_favourites.GetValue() is True:
            print("TODO: Add this problem to favorites")

        self.EndModal(wx.ID_OK)


    def _on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)


    def _modifier_decorator(self, modifier_item):
        return "{0} - {1}".format(modifier_item.code_short,
                                  modifier_item.preferred)


    def _search_result_decorator(self, result_object, query_string):
        code_str = unicode(result_object.code)
        title_str = unicode(result_object.preferred_plain)

        if len(query_string) != 0:
            result = re.search(re.escape(query_string), code_str, re.IGNORECASE)
            if result is not None:
                group = unicode(result.group())
                code_str = string.replace(code_str, group, u'<b>' + group + u'</b>', 1)

        for word in query_string.split():
            result = re.search(re.escape(word), title_str, re.IGNORECASE)
            if result is not None:
                group = unicode(result.group())
                title_str = string.replace(title_str, group, u'<b>' + group + u'</b>', 1)


        return u'<font size="2"><table><tr><td width="45" valign="top">{0}</td><td>{1}</td></tr></table></font>'.format(
            code_str, title_str
        )


    def _on_change_left_panel(self, event):
        if wx.Platform == "__WXMSW__":
            active_page_text = self.left_panel.GetPageText(self.left_panel.GetSelection())
            if active_page_text == "Browse":
                current_class = self.category_list.get_selected_category()
                self.chapter_tree.initialize()
                if current_class is not None:
                    self.chapter_tree.set_class(current_class)
            event.Skip()
        else:
            active_page_text = self.left_panel.GetPageText(self.left_panel.GetSelection())
            if active_page_text != "Browse":
                current_class = self.category_list.get_selected_category()
                self.chapter_tree.initialize()
                if current_class is not None:
                    self.chapter_tree.set_class(current_class)
            event.Skip()


    def _on_change_filter(self, event):
        """ search and display results """
        str_search = self.txt_search.GetValue()

        if str_search == "":
            self.result_list.clear()
            return

        items = self.session.query(db.Icd10Class)

        and_filters = []

        if str_search:
            for word in str_search.split():
                if word:
                    and_filters.append(db.Icd10Class.preferred_plain.like("%{}%".format(word)))

        items = items.filter(db.Icd10Class.kind == "category").filter(
            or_(
                db.Icd10Class.code.like("%{0}%".format(str_search)),
                and_(
                    *and_filters
                )
            )
        )

        self.result_list.set_result(items, str_search)


    def _on_result_selected(self, event):
        result_selected = self.result_list.get_selected_object()

        if result_selected is None:
            return

        self.set_category(result_selected)


    def _on_tree_selected(self, event):
        tree_selected = self.chapter_tree.get_selected_class()

        if tree_selected is None:
            return

        if tree_selected.kind is not "category":
            return

        self.set_category(tree_selected)


    def _get_class_from_code(self, code):
        try:
            icd10_class = self.session.query(db.Icd10Class)\
                            .filter(db.Icd10Class.code == code)\
                            .one()
            return icd10_class
        except NoResultFound:
            return None


    def _on_link_category_list(self, event):
        link_info = event.GetLinkInfo()
        href_p = urlparse(link_info.GetHref())
        if href_p.path == "category":
            query_p = parse_qs(href_p.query)
            if "code" in query_p.keys():
                link_class = self._get_class_from_code(query_p['code'][0])
                if link_class is not None:
                    self.set_category(link_class, update_tree=True)

        print("Clicked a link href={0}".format(link_info.GetHref()))


    def _update_browser_title(self, icd10class):
        if icd10class is None:
            self.browser_title.SetPage(
                "<table><tr><td><b>International Classification of Disease - 10</b></td></tr></table>")
            return

        if icd10class.kind == "chapter":
            chapter_html = "<b>Chapter {0} {1}</b>".format(
                icd10class.code, icd10class.preferred_plain)
        else:
            try:
                chapter_code, chapter_title = \
                    self.session.query(db.Icd10Class.code, db.Icd10Class.preferred_plain)\
                        .filter(db.Icd10Class.code == icd10class.chapter_code)\
                        .one()
                chapter_html = "<b>Chapter {0} {1}</b>".format(chapter_code, chapter_title)
            except NoResultFound:
                chapter_html = ""


        if icd10class.kind == "block":
            block_html = "<b>{0} </b> {1}".format(
                icd10class.code, icd10class.preferred_plain)
        else:
            try:
                block_code, block_title = \
                    self.session.query(db.Icd10Class.code, db.Icd10Class.preferred_plain)\
                        .filter(db.Icd10Class.code == icd10class.parent_block_code)\
                        .one()

                block_html = "<b>{0} </b> {1}".format(block_code, block_title)
            except NoResultFound:
                block_html = ""

        self.browser_title.SetPage(
            '<font size="2"><table><tr><td>{0}</td></tr><tr><td>{1}</td></tr></table></font>'.format(
                chapter_html, block_html)
        )


    def _on_change_category(self, event):
        current_class = self.category_list.get_selected_category()

        if current_class is None:
            return

        self.set_category(current_class, update_tree=True)