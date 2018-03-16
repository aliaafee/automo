"""DB Query Result List Box"""
import re
import string
import wx
import wx.html


class DbQueryResultBox(wx.html.HtmlListBox):
    """Display results of sqlalchemy query, formated in HTML.
      Results are displayed in a virtual list so very large
      query results are supported without slowdown"""
    def __init__(self, parent, html_decorator=None, minimum_fetch=50, **kwds):
        super(DbQueryResultBox, self).__init__(
            parent, **kwds
        )
        self.parent = parent
        self.html_decorator = html_decorator
        self.minimum_fetch = minimum_fetch

        self.extra_row_value = None

        self.query_string = ""
        self.query_result = None
        self.query_result_count = 0
        self.SetItemCount(0)

        self.items_cache = {}

        if self.html_decorator is None:
            self.html_decorator = self._html_decorator

        if wx.Platform == "__WXMSW__":
            self.SetSelectionBackground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENUHILIGHT))
        else:
            self.SetSelectionBackground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))


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

        self.items_cache = {}

        self.ScrollToRow(0)
        if extra_row_value is None:
            self.SetItemCount(self.query_result_count)
        else:
            self.SetItemCount(self.query_result_count + 1)
        self.SetSelection(-1)

        self.Refresh()


    def _fetch_items(self, page):
        start = page * self.minimum_fetch
        items = self.query_result.offset(start).limit(self.minimum_fetch).all()
        for index, item in enumerate(items):
            self.items_cache[start+index] = item


    def get_object(self, index):
        """Return the object at the given index"""
        if index < 0 or index > self.query_result_count - 1:
            return None

        try:
            return self.items_cache[index]
        except KeyError:
            page = int(index / float(self.minimum_fetch))
            self._fetch_items(page)
            return self.items_cache[index]


    def get_selected_object(self):
        """Return the selected database object, or the first one if multiple selected"""
        if not self.HasMultipleSelection():
            return self.get_object(self.GetSelection())
        index, cookie = self.GetFirstSelected()
        return self.get_object(index)


    def get_all_selected_object(self):
        """Return all selected database objects"""
        if not self.HasMultipleSelection():
            return [self.get_selected_object()]

        selected_items = []
        current_index, cookie = self.GetFirstSelected()
        while current_index != wx.NOT_FOUND:
            selected_items.append(self.get_object(current_index))
            current_index, cookie = self.GetNextSelected(cookie)

        return selected_items


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
