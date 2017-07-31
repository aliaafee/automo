"""DB Query Result"""
import re
import string
import wx


class DbQueryResultBox(wx.HtmlListBox):
    """Display results of sqlalchemy query, formated in HTML.
      Results are displayed in a virtual list so very large
      query results are supported without slowdown or excessive
      memory usage"""
    def __init__(self, parent, html_decorator=None, minimum_fetch=50, **kwds):
        super(DbQueryResultBox, self).__init__(
            parent, **kwds
        )
        self.parent = parent
        #self.session = session
        self.html_decorator = html_decorator
        self.minimum_fetch = minimum_fetch

        self.extra_row_value = None

        self.query_string = ""
        self.query_result = None
        self.query_result_count = 0
        self.SetItemCount(0)
        self.visible_begin = -1
        self.visible_end = -1
        self.visible_items = []

        if self.html_decorator is None:
            self.html_decorator = self._html_decorator

        if wx.Platform == "__WXMSW__":
            self.SetSelectionBackground(wx.SystemSettings_GetColour(wx.SYS_COLOUR_MENUHILIGHT))
        else:
            self.SetSelectionBackground(wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT))


    def _html_decorator(self, item, query_string):
        item_str = unicode(item)

        result = re.search(re.escape(query_string), item_str, re.IGNORECASE)
        if result is not None:
            group = unicode(result.group())
            item_str = string.replace(item_str, group, u'<b>' + group + u'</b>', 1)

        return '<font size="2">{0}</format>'.format(item_str)


    def clear(self):
        """Remove all items from list"""
        self.SetItemCount(0)
        self.query_result = None
        self.Refresh()


    def set_result(self, query_result, query_string="", extra_row_value=None):
        """Set the sqlalchemy query result."""
        self.query_string = query_string
        self.query_result = query_result
        self.query_result_count = self.query_result.count()
        self.extra_row_value = extra_row_value

        self.visible_begin = -1
        self.visible_end = -1
        self.visible_items = []

        self.ScrollToRow(0)
        if extra_row_value is None:
            self.SetItemCount(self.query_result_count)
        else:
            self.SetItemCount(self.query_result_count + 1)
        self.SetSelection(-1)

        self.Refresh()


    def get_object(self, index, get_uncached=False):
        """Return the object at the given index"""
        if index < 0 or index > self.query_result_count - 1:
            return None

        visible_index = index - self.visible_begin
        try:
            return self.visible_items[visible_index]
        except IndexError:
            start = self.GetVisibleRowsBegin()
            end = self.GetVisibleRowsEnd()

            if end != self.visible_end:
                if end - start > self.minimum_fetch:
                    if end != self.visible_end:
                        self._fetch_visible()
                else:
                    if start != self.visible_begin:
                        self._fetch_visible()
            
            visible_index = index - self.visible_begin
            try:
                return self.visible_items[visible_index]
            except IndexError:
                if not get_uncached:
                    return None

                item = self.query_result\
                        .offset(index)\
                        .limit(1).one()

                return item


    def get_selected_object(self):
        """Return the selected database object, or the first one if multiple selected"""
        return self.get_object(self.GetSelection(), True)


    def get_all_selected_object(self):
        """Return all selected database objects"""
        if not self.HasMultipleSelection():
            return self.get_selected_object()

        selected_items = []
        current_index, cookie = self.GetFirstSelected()
        while current_index != wx.NOT_FOUND:
            selected_items.append(self.get_object(current_index, True))
            current_index, cookie = self.GetNextSelected(cookie)

        return selected_items


    def _fetch_visible(self):
        self.visible_begin = self.GetVisibleRowsBegin()
        self.visible_end = self.GetVisibleRowsEnd()

        row_limit = self.visible_end - self.visible_begin
        row_limit = self.minimum_fetch if row_limit < self.minimum_fetch else row_limit

        self.visible_items = self.query_result\
                                .offset(self.visible_begin)\
                                .limit(row_limit).all()


    def OnGetItem(self, n):
        """Return the nth row of the list for display"""
        if self.query_result is None:
            return ""

        if n > self.query_result_count - 1:
            if self.extra_row_value is not None:
                return self.extra_row_value
            return ""

        item = self.get_object(n)

        if item is None:
            return "<broken>"

        if self.html_decorator is None:
            return unicode(item)

        return self.html_decorator(item, self.query_string)
