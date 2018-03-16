"""DB Combo Result"""
import wx
import wx.html


class DbComboBox(wx.ComboBox):
    """DB Combo Result"""
    def __init__(self, parent, html_decorator=None, minimum_fetch=50,
                 style=wx.SUNKEN_BORDER, **kwds):
        super(DbComboBox, self).__init__(
            parent, style=wx.CB_READONLY, **kwds
        )

        self.minimum_fetch = 50
        self.items_iterable = None
        self.items = []
        self.html_decorator = html_decorator

        if self.html_decorator is None:
            self.html_decorator = self._default_decorator


    def _default_decorator(self, item):
        return unicode(item)


    def get_selected_item(self):
        selection = self.GetSelection()

        if selection == wx.NOT_FOUND:
            return None

        try:
            return self.items[selection]
        except IndexError:
            return None


    def clear(self):
        """Clear all items in list"""
        self.items_iterable = None
        self.items = []
        self.Clear()


    def set_selected_item(self, selected_item):
        """Set selection to database item"""
        if self.items_iterable is None or len(self.items) == 0:
            return

        list_index = 0
        for item in self.items:
            if item == selected_item:
                self.SetSelection(list_index)
            list_index += 1


    def set_items(self, items_iterable):
        """Set items from iterable list of items"""
        self.items_iterable = items_iterable

        self.items = []
        item_strs = []
        for item in self.items_iterable:
            self.items.append(item)
            item_strs.append(self.html_decorator(item))

        self.Clear()

        self.SetItems(item_strs)
