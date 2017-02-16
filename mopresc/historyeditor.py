import wx
from wx.lib.wordwrap import wordwrap
from ObjectListView import ObjectListView, ColumnDefn, OLVEvent

from images import *
from objectlistviewmod import ObjectListViewMod


class HistoryEditor(wx.Dialog):
    def __init__(self, parent, session, historyTable, **kwds):
        super(HistoryEditor, self).__init__(parent, **kwds)

        self.session = session
        self.historyTable = historyTable

        self.historyList = ObjectListViewMod( 
                self, 
                style=wx.LC_REPORT|wx.SUNKEN_BORDER, 
                cellEditMode=ObjectListView.CELLEDIT_DOUBLECLICK 
        )

        self.historyList.SetColumns([
            ColumnDefn("", "", 0, "id", isEditable = False),
            ColumnDefn(self.GetTitle(), "left", 300, "name", isEditable = True)
        ])
        
        self.historyList.SetEmptyListMsg("")
        self.historyList.useAlternateBackColors = False
        self.historyList.Bind(OLVEvent.EVT_CELL_EDIT_FINISHED, self.OnCellEditFinished)
        self.historyList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnHistoryContextMenu)

        self.historyMenu = wx.Menu()
        id = 700
        self.historyMenu.Append(id, "Remove", "Remove Item From History")
        wx.EVT_MENU(self, id,  self.OnRemoveItem)

        self.UpdateList()


    def UpdateList(self):
        self.historyList.DeleteAllItems ()
        
        for item in self.session.query(self.historyTable).order_by(self.historyTable.name):
            self.historyList.AddObject(item)
           
        self.historyList.RefreshObjects(self.historyList.GetObjects())


    def OnRemoveItem(self, event):
        selectedItems = self.historyList.GetSelectedObjects()

        if len(selectedItems) < 1:
            return

        dlg = wx.MessageDialog(None, 'Remove selected items from history?', 'Remove Items', 
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        result = dlg.ShowModal()

        if (result != wx.ID_YES):
            return

        for item in selectedItems:
            self.session.delete(item)

        self.session.commit()

        self.UpdateList()


    def OnHistoryContextMenu(self, event):
        self.PopupMenu(self.historyMenu)


    def OnCellEditFinished(self, event):
        self.session.commit()
