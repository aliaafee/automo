"""
DB Combo Result
"""
import wx
import wx.html

from dbqueryresultbox import DbQueryResultBox

class DbComboBox(wx.ComboBox):
    def __init__(self, parent, session, html_decorator=None, minimum_fetch=50,
                 style=wx.SUNKEN_BORDER, **kwds):
        super(DbComboBox, self).__init__(
            parent, style=wx.CB_READONLY, **kwds
        )

        self.session = session
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
        self.ChangeValue("")


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




def main():
    import database
    def decor(item):
        return "{0} - {1}".format(item.code_short, item.preferred)

    database.StartEngine("sqlite:///wardpresc-data.db", False, "")
    session = database.Session()

    app = wx.PySimpleApp(0)

    dlg = wx.Dialog(None)

    sizer = wx.BoxSizer(wx.VERTICAL)
    cmb = DbComboBox(dlg, session, decor)

    def on_change(event):
        print cmb.get_selected_item()

    cmb.Bind(wx.EVT_COMBOBOX, on_change)
    txt = wx.TextCtrl(dlg)

    sizer.Add(txt, 0, wx.EXPAND | wx.ALL, border=5)
    sizer.Add(cmb, 0, wx.EXPAND | wx.ALL, border=5)
    sizer.AddStretchSpacer()

    dlg.SetSizer(sizer)

    mod = session.query(database.Icd10Modifier)\
            .filter(database.Icd10Modifier.code == "J96_5")\
            .one()

    #classes = mod.classes


    classes = session.query(database.Icd10ModifierClass)\
                        .filter(database.Icd10ModifierClass.modifier_code == "J96_5")

    cmb.set_items(classes)

    que = session.query(database.Icd10ModifierClass)\
            .filter(database.Icd10ModifierClass.code == "J96_51")\
            .one()

    cmb.set_selected_item(que)

    app.SetTopWindow(dlg)
    dlg.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()