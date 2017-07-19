"""HistoryEditor dialog, to edit drug history and diagnosis history"""

import wx
from ObjectListView import ObjectListView, ColumnDefn, OLVEvent

from objectlistviewmod import ObjectListViewMod
from images import bitmap_from_base64,\
                   toolbar_filter_24_b64


class HistoryEditor(wx.Dialog):
    """Dialog to edit a history table with 'name' column.
      TODO: Repurpose for version 2, currently does nothing."""
    def __init__(self, parent, session, history_table, size=wx.Size(-1, 400), **kwds):
        super(HistoryEditor, self).__init__(
            parent, style=wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION,
            size=size, **kwds)

        self.session = session
        self.history_table = history_table

        grid_sizer = wx.GridBagSizer(0, 0)

        self.btn_filter = wx.BitmapButton(self, bitmap=bitmap_from_base64(toolbar_filter_24_b64),
                                          style=wx.BU_AUTODRAW, size=wx.Size(24, 24))
        self.btn_filter.SetToolTipString("Filter")
        self.btn_filter.Bind(wx.EVT_BUTTON, self._on_change_filter)
        grid_sizer.Add(self.btn_filter, wx.GBPosition(0, 0),
                       flag=wx.LEFT | wx.BOTTOM | wx.TOP | wx.ALIGN_CENTER_VERTICAL, border=5)

        self.txt_filter = wx.TextCtrl(self)
        self.txt_filter.Bind(wx.EVT_TEXT, self._on_change_filter)
        grid_sizer.Add(self.txt_filter, wx.GBPosition(0, 1), flag=wx.EXPAND | wx.ALL, border=5)

        self.history_list = ObjectListViewMod(
            self,
            style=wx.LC_REPORT|wx.SUNKEN_BORDER,
            cellEditMode=ObjectListView.CELLEDIT_DOUBLECLICK
        )
        grid_sizer.Add(self.history_list, wx.GBPosition(1, 0), wx.GBSpan(2, 2),
                       flag=wx.EXPAND | wx.ALL, border=0)

        self.history_list.SetColumns([
            ColumnDefn("", "", 0, "id", isEditable=False),
            ColumnDefn(self.GetTitle(), "left", 300, "name", isEditable=True)
        ])

        self.history_list.SetEmptyListMsg("")
        self.history_list.useAlternateBackColors = False
        self.history_list.Bind(OLVEvent.EVT_CELL_EDIT_FINISHED, self._on_cell_edit_finished)
        self.history_list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self._on_history_context_menu)

        self.history_menu = wx.Menu()
        menu_id = 700
        self.history_menu.Append(menu_id, "Remove", "Remove Item From History")
        wx.EVT_MENU(self, menu_id, self.on_remove_item)

        grid_sizer.AddGrowableCol(1)
        grid_sizer.AddGrowableRow(1)
        self.SetSizer(grid_sizer)

        self.txt_filter.SetFocus()

        self.update_list()


    def update_list(self):
        """ Updates the history list """
        self.history_list.DeleteAllItems()

        items = self.session.query(self.history_table)

        str_filter = self.txt_filter.GetValue()
        if str_filter != "":
            items = items.filter(self.history_table.name.like("%{0}%".format(str_filter)))

        items = items.order_by(self.history_table.name)

        for item in items:
            self.history_list.AddObject(item)

        self.history_list.RefreshObjects(self.history_list.GetObjects())


    def on_remove_item(self, event):
        """ Remove history item """
        selected_items = self.history_list.GetSelectedObjects()

        if len(selected_items) < 1:
            return

        dlg = wx.MessageDialog(None, 'Remove selected items from history?', 'Remove Items',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        result = dlg.ShowModal()

        if result != wx.ID_YES:
            return

        for item in selected_items:
            self.session.delete(item)

        self.session.commit()

        self.update_list()


    def _on_history_context_menu(self, event):
        self.PopupMenu(self.history_menu)


    def _on_cell_edit_finished(self, event):
        self.session.commit()


    def _on_change_filter(self, event):
        self.update_list()
        
