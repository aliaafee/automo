"""
Condition Panel
"""
import wx

import images
from database import Drug
from acdbtextctrl import AcDbTextCtrl
from objectlistviewmod import ObjectListViewMod, EVT_OVL_CHECK_EVENT
from ObjectListView import ObjectListView, ColumnDefn, OLVEvent


class PrescriptionPanel(wx.Panel):
    """
    Prescription Panel
    """
    def __init__(self, parent, session, **kwds):
        super(PrescriptionPanel, self).__init__(parent, **kwds)

        self.session = session
        self.admission = None

        self.changed = False
        self.editable = True

        #self.toolbar = wx.ToolBar(self, style=wx.TB_NODIVIDER)
        #self.toolbar.AddLabelTool(wx.ID_SAVE, "Save", images.get("save"),
        #                          wx.NullBitmap, wx.ITEM_NORMAL, "Save changes", "")
        #self.toolbar.Bind(wx.EVT_TOOL, self._on_save, id=wx.ID_SAVE)
        #self.toolbar.Realize()

        self.drug_add_panel = wx.Panel(self)

        lbl_from_date = wx.StaticText(self.drug_add_panel, label="From", size=wx.Size(-1, -1))
        self.txt_from_date = wx.DatePickerCtrl(self.drug_add_panel, style=wx.DP_DROPDOWN)

        lbl_to_date = wx.StaticText(self.drug_add_panel, label="To", size=wx.Size(-1, -1))
        self.txt_to_date = wx.DatePickerCtrl(self.drug_add_panel, style=wx.DP_DROPDOWN | wx.DP_ALLOWNONE)

        lbl_drug_name = wx.StaticText(self.drug_add_panel, label="Medication", size=wx.Size(-1, -1))
        self.txt_drug_name = AcDbTextCtrl(self.drug_add_panel, self.session, Drug)

        lbl_drug_order = wx.StaticText(self.drug_add_panel, label="Order", size=wx.Size(-1, -1))
        self.txt_drug_order = wx.TextCtrl(self.drug_add_panel)

        self.btn_add = wx.BitmapButton(self.drug_add_panel, bitmap=images.get('add'),
                                       style=wx.BU_AUTODRAW, size=wx.Size(24, 24))
        self.btn_add.SetToolTipString("Add Medication")
        self.btn_add.Bind(wx.EVT_BUTTON, self._on_add_drug)

        self.btn_preset = wx.Button(self.drug_add_panel, label="...", size=wx.Size(24, 24))
        self.btn_preset.SetToolTipString("Add Preset")
        self.btn_preset.Bind(wx.EVT_BUTTON, self._on_add_preset)

        grid_sizer = wx.FlexGridSizer(2, 6, 2, 2)
        grid_sizer.AddMany([
            lbl_from_date,
            lbl_to_date,
            lbl_drug_name,
            lbl_drug_order
        ])
        grid_sizer.AddSpacer(1)
        grid_sizer.AddSpacer(1)
        grid_sizer.AddMany([
            (self.txt_from_date, 1, wx.EXPAND),
            (self.txt_to_date, 1, wx.EXPAND),
            (self.txt_drug_name, 1, wx.EXPAND),
            (self.txt_drug_order, 1, wx.EXPAND),
            (self.btn_add, 1, wx.EXPAND),
            (self.btn_preset, 1, wx.EXPAND)
        ])
        grid_sizer.AddGrowableCol(2)
        grid_sizer.AddGrowableCol(3)
        self.drug_add_panel.SetSizer(grid_sizer)

        self.prescription_list = ObjectListViewMod(
            self,
            style=wx.LC_REPORT|wx.SUNKEN_BORDER,
            cellEditMode=ObjectListView.CELLEDIT_DOUBLECLICK
        )
        self.prescription_list.SetEmptyListMsg("")
        self.prescription_list.useAlternateBackColors = False
        self.prescription_list.Bind(EVT_OVL_CHECK_EVENT, self._on_prescription_check)
        self.prescription_list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self._on_prescription_context)
        self.prescription_list.Bind(OLVEvent.EVT_CELL_EDIT_FINISHED, self._on_prescription_order_edit)

        sizer = wx.BoxSizer(wx.VERTICAL)
        #sizer.Add(self.toolbar, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        sizer.Add(self.drug_add_panel, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        sizer.Add(self.prescription_list, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(sizer)

        self.prescription_menu = wx.Menu()
        self.prescription_menu.Append(wx.ID_REMOVE, "Remove", "Remove Medication.")
        self.prescription_menu.Append(wx.ID_SELECTALL, "Tick All", "Tick All Medications")
        self.prescription_menu.Append(wx.ID_CLEAR, "Untick All", "Untick All Medications")
        self.prescription_menu.Bind(wx.EVT_MENU, self._on_remove_medication, id=wx.ID_REMOVE)
        self.prescription_menu.Bind(wx.EVT_MENU, self._on_tick_all_medication, id=wx.ID_SELECTALL)
        self.prescription_menu.Bind(wx.EVT_MENU, self._on_untick_all_medication, id=wx.ID_CLEAR)


    def _on_save(self, event):
        self.save_changes()


    def _has_changed(self):
        self.changed = True
        #self.toolbar.EnableTool(wx.ID_SAVE, True)


    def _on_add_drug(self, event):
        pass

    
    def _on_add_preset(self, event):
        pass


    def _on_prescription_check(self, event):
        if event.value is True:
            event.object.active = True
        else:
            event.object.active = False
        self.session.commit()


    def _on_prescription_order_edit(self, event):
        self.session.commit()


    def _on_prescription_context(self, event):
        if self.editable:
            self.PopupMenu(self.prescription_menu)


    def _on_tick_all_medication(self, event):
        items = self.prescription_list.GetObjects()
        for item in items:
            item.active = True
            self.prescription_list.SetCheckState(item, True)

        self.session.commit()
        self.prescription_list.RefreshObjects(items)


    def _on_untick_all_medication(self, event):
        items = self.prescription_list.GetObjects()
        for item in items:
            item.active = False
            self.prescription_list.SetCheckState(item, False)

        self.session.commit()
        self.prescription_list.RefreshObjects(items)


    def _on_remove_medication(self, event):
        dlg = wx.MessageDialog(None, 'Remove selected medications?', 'Remove Medication',
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        result = dlg.ShowModal()

        if result != wx.ID_YES:
            return

        for item in self.prescription_list.GetSelectedObjects():
            self.session.delete(item)

        self.session.commit()

        self._refresh_prescription()


    def _refresh_prescription(self):
        self.prescription_list.DeleteAllItems()

        if self.admission is None:
            return

        for item in self.admission.prescription:
            self.prescription_list.AddObject(item)
            if item.active:
                self.prescription_list.SetCheckState(item, True)
            else:
                self.prescription_list.SetCheckState(item, False)

        self.prescription_list.RefreshObjects(self.prescription_list.GetObjects())


    def set_editable(self, editable):
        """Set control to editable or not"""
        self.editable = editable

        if self.editable:
            #self.toolbar.Show()
            self.drug_add_panel.Show()
            self.prescription_list.SetColumns([
                ColumnDefn("From", "left", 90, "date_from", isEditable=False),
                ColumnDefn("To", "left", 90, "date_to", isEditable=False),
                ColumnDefn("Medication", "left", 180, "drug", isEditable=False),
                ColumnDefn("Order", "left", 140, "drug_order")
            ])
            self.prescription_list.CreateCheckStateColumn()
        else:
            #self.toolbar.Hide()
            self.drug_add_panel.Hide()
            self.prescription_list.SetColumns([
                ColumnDefn("From", "left", 90, "date_from", isEditable=False),
                ColumnDefn("To", "left", 90, "date_to", isEditable=False),
                ColumnDefn("Medication", "left", 180, "drug", isEditable=False),
                ColumnDefn("Order", "left", 140, "drug_order", isEditable=False)
            ])

        self.Layout()


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing.
          Always false in this panel as all changes are autosaved"""
        return False


    def save_changes(self):
        """Save changes. Everything is auto saved."""
        pass


    def set_admission(self, admission, editable=True):
        """Set the current admission"""
        self.admission = admission

        self.set_editable(editable)

        self._refresh_prescription()

        self.changed = False
        #self.toolbar.EnableTool(wx.ID_SAVE, False)
