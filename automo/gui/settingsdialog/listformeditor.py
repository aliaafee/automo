"""List with form view for data editing"""
import wx

from .. import images
from .. import events
from ..widgets import DbQueryResultBox
from ..dbform import FormPanel


class ListFormEditor(wx.Panel):
    """List with form view for data editing"""
    def __init__(self, parent, session, db_class, fields, **kwds):
        super(ListFormEditor, self).__init__(parent, **kwds)

        self.session = session
        self.db_class = db_class
        self.fields = fields

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)
        self.create_toolbar()
        self.toolbar.Realize()

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self.data_list = DbQueryResultBox(splitter, style=wx.LB_MULTIPLE)
        self.data_list.Bind(wx.EVT_LISTBOX, self._on_list_item_selected)
        self.data_list.Bind(wx.EVT_RIGHT_DOWN, self._on_list_item_context)

        self._left_panel = wx.Panel(splitter, style=wx.BORDER_THEME)

        self.data_form = FormPanel(self._left_panel, self.db_class, fields, scrollable=False)
        self.data_form.Bind(events.EVT_AM_DB_FORM_CHANGED, self._on_field_changed)

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(self.data_form, 0, wx.EXPAND | wx.ALL, border=5)
        self._left_panel.SetSizer(left_sizer)

        splitter.SplitVertically(self.data_list, self._left_panel, 200)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolbar, 0, wx.EXPAND)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.list_item_menu = wx.Menu()
        self.list_item_menu.Append(wx.ID_REMOVE, "Remove", "Remove Selected Item.")
        self.list_item_menu.Bind(wx.EVT_MENU, self._on_remove_list_item, id=wx.ID_REMOVE)

        self.selected_item = None
        self.data_form.Hide()
        self.update_list()


    def create_toolbar(self):
        self.toolbar.AddTool(wx.ID_ADD, "Add", images.get("add_24"), wx.NullBitmap, wx.ITEM_NORMAL, "Add", "")
        self.toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)


    def update_list(self):
        result = self.session.query(self.db_class)
        self.data_list.set_result(result)


    def _on_add(self, event):
        new_item = self.db_class()
        self.session.add(new_item)
        self.session.commit()
        self.update_list()
        self.set_selected_item(new_item)


    def set_selected_item(self, item):
        self.selected_item = item

        if self.selected_item is None:
            self.data_form.Hide()
            return

        self.data_form.Show()
        self.data_form.set_object(self.selected_item)

        self._left_panel.Layout()
    

    def _on_list_item_selected(self, event):
        self.set_selected_item(self.data_list.get_selected_object())

    
    def _on_list_item_context(self, event):
        self.PopupMenu(self.list_item_menu)


    def _on_field_changed(self, event):
        self.data_form.update_object(self.selected_item)
        self.session.commit()
        self.data_list.RefreshAll()


    def _on_remove_list_item(self, event):
        with wx.MessageDialog(self, 'Remove selected item(s)?', 'Remove Item',
                              wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) as dlg:
            dlg.CenterOnParent()
            if dlg.ShowModal() == wx.ID_YES:
                selected = self.data_list.get_all_selected_object()
                for item in selected:
                    self.session.delete(item)
                self.session.commit()
                self.update_list()

            
