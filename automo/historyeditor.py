"""
HistoryEditor dialog, to edit drug history and diagnosis history
"""

import wx
from ObjectListView import ObjectListView, ColumnDefn, OLVEvent

from objectlistviewmod import ObjectListViewMod


class HistoryEditor(wx.Dialog):
    """
    Dialog to edit a history table with 'name' column.
    """
    def __init__(self, parent, session, history_table, **kwds):
        super(HistoryEditor, self).__init__(parent, **kwds)

        self.session = session
        self.history_table = history_table

        self.history_list = ObjectListViewMod(
            self,
            style=wx.LC_REPORT|wx.SUNKEN_BORDER,
            cellEditMode=ObjectListView.CELLEDIT_DOUBLECLICK
        )

        self.history_list.SetColumns([
            ColumnDefn("", "", 0, "id", isEditable=False),
            ColumnDefn(self.GetTitle(), "left", 300, "name", isEditable=True)
        ])

        self.history_list.SetEmptyListMsg("")
        self.history_list.useAlternateBackColors = False
        self.history_list.Bind(OLVEvent.EVT_CELL_EDIT_FINISHED, self.on_cell_edit_finished)
        self.history_list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.on_history_context_menu)

        self.history_menu = wx.Menu()
        menu_id = 700
        self.history_menu.Append(menu_id, "Remove", "Remove Item From History")
        wx.EVT_MENU(self, menu_id, self.on_remove_item)

        self.update_list()


    def update_list(self):
        """ Updates the history list """
        self.history_list.DeleteAllItems()

        for item in self.session.query(self.history_table).order_by(self.history_table.name):
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


    def on_history_context_menu(self, event):
        self.PopupMenu(self.history_menu)


    def on_cell_edit_finished(self, event):
        self.session.commit()
