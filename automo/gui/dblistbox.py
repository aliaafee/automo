"""DB Query Result"""
import re
import string
import wx
import wx.html


class DbListBox(wx.html.HtmlListBox):
    """Display iterable list of objects with formatting"""
    def __init__(self, parent, html_decorator=None, **kwds):
        super(DbListBox, self).__init__(
            parent, **kwds
        )
        self.parent = parent

        self.html_decorator = html_decorator

        self.items_count = 0
        self.items = []
        self.extra_row_value = None

        if self.html_decorator is None:
            self.html_decorator = self._html_decorator

        if wx.Platform == "__WXMSW__":
            self.SetSelectionBackground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENUHILIGHT))
        else:
            self.SetSelectionBackground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT))


    def _html_decorator(self, item):
        item_str = unicode(item)

        return '<font size="2">{0}</format>'.format(item_str)


    def clear(self):
        """Remove all items from list"""
        self.SetItemCount(0)
        self.items = []
        self.items_count = 0
        self.Refresh()


    def set_items(self, items, extra_row_value=None):
        """Set the sqlalchemy query result."""
        self.items = items
        self.items_count = len(items)
        self.extra_row_value = extra_row_value

        if extra_row_value is None:
            self.SetItemCount(self.items_count)
        else:
            self.SetItemCount(self.items_count + 1)
        
        self.ScrollToRow(0)
        self.SetSelection(-1)
        self.Refresh()


    def get_object(self, index):
        """Return the object at the given index"""
        if index < 0 or index > self.items_count - 1:
            return None

        return self.items[index]


    def get_selected_object(self):
        """Return the selected database object, or the first one if multiple selected"""
        return self.get_object(self.GetSelection())


    def get_all_selected_object(self):
        """Return all selected database objects"""
        if not self.HasMultipleSelection():
            return self.get_selected_object()

        selected_items = []
        current_index, cookie = self.GetFirstSelected()
        while current_index != wx.NOT_FOUND:
            selected_items.append(self.get_object(current_index))
            current_index, cookie = self.GetNextSelected(cookie)

        return selected_items


    def OnGetItem(self, n):
        """Return the nth row of the list for display"""
        if n > self.items_count - 1:
            if self.extra_row_value is not None:
                return self.extra_row_value
            return ""

        if self.items_count == 0:
            return ""

        item = self.get_object(n)

        if item is None:
            return "<broken>"

        if self.html_decorator is None:
            return unicode(item)

        return self.html_decorator(item)
