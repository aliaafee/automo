"""Base Prescription Panel"""
import wx
from ObjectListView import ObjectListView, ColumnDefn, OLVEvent

from . import images
from .. import database as db
from .widgets import AcDbTextCtrl, ObjectListViewMod, EVT_OVL_CHECK_EVENT


ID_PRESET_ADD = wx.NewId()
ID_PRESET_REMOVE = wx.NewId()


class BasePrescriptionPanel(object):
    """Prescription Panel"""
    def __init__(self, parent, session, **kwds):
        super(BasePrescriptionPanel, self).__init__(parent, session, **kwds)
        self.session = session

        self.preset_add_id_object = {}
        self.preset_remove_id_object = {}

        self.drug_add_panel = wx.Panel(self)

        lbl_drug_name = wx.StaticText(self.drug_add_panel, label="Medication", size=wx.Size(-1, -1))
        self.txt_drug_name = AcDbTextCtrl(self.drug_add_panel, self.session, db.Drug)
        self.txt_drug_name.Bind(wx.EVT_KEY_UP, self._on_drug_name_keyup)

        lbl_drug_order = wx.StaticText(self.drug_add_panel, label="Order", size=wx.Size(-1, -1))
        self.txt_drug_order = AcDbTextCtrl(self.drug_add_panel, self.session, None)
        self.txt_drug_order.Bind(wx.EVT_KEY_UP, self._on_drug_order_keyup)

        self.btn_add = wx.BitmapButton(self.drug_add_panel, bitmap=images.get('add'),
                                       style=wx.BU_AUTODRAW, size=wx.Size(24, 24))
        self.btn_add.SetToolTip("Add Medication")
        self.btn_add.Bind(wx.EVT_BUTTON, self._on_add_drug)

        self.btn_preset = wx.Button(self.drug_add_panel, label="...", size=wx.Size(24, 24))
        self.btn_preset.SetToolTip("Add Preset")
        self.btn_preset.Bind(wx.EVT_BUTTON, self._on_preset_menu)

        grid_sizer = wx.FlexGridSizer(2, 4, 2, 2)
        grid_sizer.AddMany([
            lbl_drug_name,
            lbl_drug_order
        ])
        grid_sizer.AddSpacer(1)
        grid_sizer.AddSpacer(1)
        grid_sizer.AddMany([
            (self.txt_drug_name, 1, wx.EXPAND),
            (self.txt_drug_order, 1, wx.EXPAND),
            (self.btn_add, 1, wx.EXPAND),
            (self.btn_preset, 1, wx.EXPAND)
        ])
        grid_sizer.AddGrowableCol(0)
        grid_sizer.AddGrowableCol(1)
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
    
        self.sizer.Add(self.drug_add_panel, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        self.sizer.Add(self.prescription_list, 1, wx.EXPAND | wx.ALL, border=5)

        self.prescription_menu = wx.Menu()
        self.prescription_menu.Append(wx.ID_REMOVE, "Remove", "Remove Medication.")
        self.prescription_menu.Append(wx.ID_SELECTALL, "Tick All", "Tick All Medications")
        self.prescription_menu.Append(wx.ID_CLEAR, "Untick All", "Untick All Medications")
        self.prescription_menu.Bind(wx.EVT_MENU, self._on_remove_medication, id=wx.ID_REMOVE)
        self.prescription_menu.Bind(wx.EVT_MENU, self._on_tick_all_medication, id=wx.ID_SELECTALL)
        self.prescription_menu.Bind(wx.EVT_MENU, self._on_untick_all_medication, id=wx.ID_CLEAR)

        self.prescription_list.SetColumns([
            ColumnDefn("Medication", "left", 180, "drug", isEditable=False),
            ColumnDefn("Order", "left", 140, "drug_order", isEditable=True)
        ])


    def add_item(self, selected_drug, selected_drug_str, order_str, active=True):
        """To be overidden: Add the drug to data store"""
        pass


    def remove_item(self, item):
        """ToBe Override"""
        pass

    def get_prescription(self):
        """To be overidden: Get prescription from store"""
        return []


    def set_item_active(self, item, state=True):
        """To be overidden: Activate/Deactive the object in store"""
        pass


    def set_item_order(self, item, drug_order):
        """To be overidden: Set the order for the item"""
        pass


    def _on_drug_name_keyup(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txt_drug_order.SetFocus()
            self.txt_drug_order.SelectAll()


    def _on_drug_order_keyup(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self._on_add_drug(event)


    def _on_add_drug(self, event):
        selected_drug = self.txt_drug_name.get_selected_object()
        selected_drug_str = self.txt_drug_name.GetValue().upper()
        order_str = self.txt_drug_order.GetValue().upper()

        if selected_drug is None and selected_drug_str == "":
            self.txt_drug_name.SetFocus()
            return

        self.add_item(selected_drug, selected_drug_str, order_str)
        
        self._refresh_prescription()
        self.txt_drug_name.Clear()
        self.txt_drug_order.Clear()
        self.txt_drug_name.SetFocus()


    def _on_preset_menu(self, event):
        preset_menu = wx.Menu()

        self.preset_add_id_object = {}
        menu_id = ID_PRESET_ADD * 100
        for preset in self.session.query(db.PresetPrescription).order_by(db.PresetPrescription.name):
            preset_menu.Append(menu_id, preset.name)
            preset_menu.Bind(wx.EVT_MENU, self._on_select_preset, id=menu_id)
            self.preset_add_id_object[menu_id] = preset
            menu_id += 1

        preset_menu.AppendSeparator()

        preset_menu.Append(ID_PRESET_ADD, "Add Current", "Add current prescription to presets.")
        preset_menu.Bind(wx.EVT_MENU, self._on_add_preset, id=ID_PRESET_ADD)

        remove_menu = wx.Menu()

        self.preset_remove_id_object = {}
        menu_id = ID_PRESET_REMOVE  * 100
        for preset in self.session.query(db.PresetPrescription).order_by(db.PresetPrescription.name):
            remove_menu.Append(menu_id, preset.name)
            self.Bind(wx.EVT_MENU, self._on_remove_preset, id=menu_id)
            self.preset_remove_id_object[menu_id] = preset
            menu_id += 1

        preset_menu.AppendSubMenu(remove_menu, "Remove", "Remove prescription preset.")

        event.GetEventObject().PopupMenu(preset_menu)


    def _on_select_preset(self, event):
        preset = self.preset_add_id_object[event.GetId()]
        for medication in preset.medications:
            self.add_item(medication.drug, "", medication.drug_order, True)
        #self.session.commit()
        self._refresh_prescription()


    def _on_remove_preset(self, event):
        preset = self.preset_remove_id_object[event.GetId()]
        self.session.delete(preset)
        self.session.commit()


    def _on_add_preset(self, event):
        """Add Current Prescription to presets"""
        name = u""
        with wx.TextEntryDialog(self, "Name", "Add Precscription Preset") as dlg:
            dlg.ShowModal()
            name = dlg.GetValue()

        if name == "":
            return

        if self.session.query(db.PresetPrescription).filter(db.PresetPrescription.name == name).count() != 0:
            dlg = wx.MessageDialog(self, 'The name "{0}" exists. Cannot add'.format(name),
                                   'Add Preset',
                                   wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            return

        new_preset = db.PresetPrescription(name=name)
        self.session.add(new_preset)
        self.session.flush()

        for item in self.get_prescription():
            new_medication = db.PresetMedication(
                drug = item.drug,
                drug_order = item.drug_order
            )
            new_preset.medications.append(new_medication)

        self.session.commit()


    def _on_prescription_check(self, event):
        if event.value is True:
            self.set_item_active(event.object, True)
        else:
            self.set_item_active(event.object, False)


    def _on_prescription_order_edit(self, event):
        pass


    def _on_prescription_context(self, event):
        #if not self.editable:
        #    return
        self.PopupMenu(self.prescription_menu)


    def _on_tick_all_medication(self, event):
        items = self.get_prescription()
        for item in items:
            self.set_item_active(item, True)

        self._refresh_prescription()


    def _on_untick_all_medication(self, event):
        items = self.get_prescription()
        for item in items:
            self.set_item_active(item, False)

        self._refresh_prescription()


    def _on_remove_medication(self, event):
        with wx.MessageDialog(self, 'Remove selected medications?', 'Remove Medication',
                              wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) as dlg:
            dlg.CenterOnParent()
            result = dlg.ShowModal()

            if result != wx.ID_YES:
                return

            for item in self.prescription_list.GetSelectedObjects():
                #self.session.delete(item)
                self.remove_item(item)

            #self.session.commit()

            self._refresh_prescription()


    def _refresh_prescription(self):
        self.prescription_list.DeleteAllItems()

        for item in self.get_prescription():
            self.prescription_list.AddObject(item)
            if item.active:
                self.prescription_list.SetCheckState(item, True)
            else:
                self.prescription_list.SetCheckState(item, False)

        self.prescription_list.RefreshObjects(self.prescription_list.GetObjects())

    


