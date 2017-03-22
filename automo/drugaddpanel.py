"""
Drug Add Panel, has a search box to selecte recently prescribed medications
and a text control to enter the drug order
"""
import wx

from actextcontroldb import ACTextControlDB
from database import Rx, Drug, Preset, PresetRx
from images import bitmap_from_base64,\
                   toolbar_add_24_b64


class DrugAddPanel(wx.Panel):
    """
    Drug Add Panel, has a search box to selecte recently prescribed medications
    and a text control to enter the drug order
    """
    def __init__(self, parent, session, patient_panel, **kwds):
        super(DrugAddPanel, self).__init__(parent, **kwds)

        self.session = session
        self.patient_panel = patient_panel

        top_sizer = wx.BoxSizer(wx.VERTICAL)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.lbl_drug_name = wx.StaticText(self, label="Medication", size=wx.Size(-1, -1))
        sizer.Add(self.lbl_drug_name, 1, wx.RIGHT | wx.TOP | wx.EXPAND, border=5)

        self.lbl_drug_order = wx.StaticText(self, label="Order", size=wx.Size(-1, -1))
        sizer.Add(self.lbl_drug_order, 1, wx.RIGHT | wx.TOP | wx.EXPAND, border=5)

        self.lbl_add = wx.StaticText(self, label=" ", size=wx.Size(50, -1))
        sizer.Add(self.lbl_add, 0, wx.TOP, border=5)

        top_sizer.Add(sizer, 1, wx.EXPAND)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.txt_drug_name = ACTextControlDB(self, self.session, Drug)
        self.txt_drug_name.Bind(wx.EVT_KEY_UP, self.OnDrugNameKeyUp)
        sizer.Add(self.txt_drug_name, 1, wx.RIGHT | wx.BOTTOM | wx.EXPAND, border=5)

        self.txt_drug_order = wx.TextCtrl(self, size=wx.Size(-1, -1))
        self.txt_drug_order.Bind(wx.EVT_KEY_UP, self.OnDrugOrderKeyUp)
        sizer.Add(self.txt_drug_order, 1, wx.RIGHT | wx.BOTTOM | wx.EXPAND, border=5)

        #self.btn_add = wx.Button(self, label="Add", size=wx.Size(50, -1))
        self.btn_add = wx.BitmapButton(self, bitmap=bitmap_from_base64(toolbar_add_24_b64),
                                       style=wx.BU_AUTODRAW, size=wx.Size(24, 24))
        self.btn_add.SetToolTipString("Add Medication")
        self.btn_add.Bind(wx.EVT_BUTTON, self.OnAddDrug)
        sizer.Add(self.btn_add, 0, wx.RIGHT | wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, border=5)

        self.btn_preset = wx.Button(self, label="...", size=wx.Size(24, 24))
        self.btn_preset.SetToolTipString("Preset Prescriptions")
        self.btn_preset.Bind(wx.EVT_BUTTON, self.OnPresetMenu)
        sizer.Add(self.btn_preset, 0, wx.BOTTOM | wx.ALIGN_CENTER_VERTICAL, border=5)

        top_sizer.Add(sizer, 1, wx.EXPAND)

        self.SetSizer(top_sizer)

        self.update_drug_list()


    def OnDrugNameKeyUp(self, event):
        """Move to next text box when enter pressed"""
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txt_drug_order.SetFocus()


    def OnDrugOrderKeyUp(self, event):
        """Move to next text box when enter pressed"""
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.OnAddDrug(event)


    def update_drug_list(self):
        """Update drug list"""
        drugs = []

        for drug in self.session.query(Drug).order_by(Drug.name):
            drugs.append(drug.name)

        self.txt_drug_name.SetCandidates(drugs)


    def OnAddDrug(self, event):
        """Add new drug"""
        drug_name = self.txt_drug_name.GetValue()
        drug_order = self.txt_drug_order.GetValue()

        if drug_name == "":
            self.txt_drug_name.SetFocus()
            self.txt_drug_name.SetSelection(-1, -1)
            return

        new_presc = Rx(patient_id=self.patient_panel.patient.id,
                       drug_name=drug_name,
                       drug_order=drug_order,
                       active=True)

        self.session.add(new_presc)
        self.session.commit()

        self.txt_drug_name.ChangeValue("")
        self.txt_drug_order.ChangeValue("")

        self.patient_panel.update_rx()

        self.txt_drug_name.SetFocus()


    def OnSelectPreset(self, event):
        """Add preset to prescription"""
        preset_name = event.GetEventObject().GetLabelText(event.GetId())
        preset = self.session.query(Preset)\
                             .filter(Preset.name == preset_name)\
                             .first()

        for row in preset.rxs:
            new_presc = Rx(patient_id=self.patient_panel.patient.id,
                           drug_name=row.drug_name,
                           drug_order=row.drug_order,
                           active=row.active)
            self.session.add(new_presc)

        self.session.commit()

        self.patient_panel.update_rx()


    def OnRemovePreset(self, event):
        """Remove preset"""
        preset_name = event.GetEventObject().GetLabelText(event.GetId())

        dlg = wx.MessageDialog(self,
                               'Remove prescription preset "{0}"?'\
                                                        .format(preset_name),
                               'Remove Prescription Preset',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        result = dlg.ShowModal()

        if result != wx.ID_YES:
            return

        preset = self.session.query(Preset)\
                             .filter(Preset.name == preset_name)\
                             .first()
        self.session.delete(preset)
        self.session.commit()


    def OnAddPreset(self, event):
        """Add current presecription to a preset"""
        dlg = wx.TextEntryDialog(self, "Name", "Add Precscription Preset", defaultValue="")
        dlg.ShowModal()
        name = dlg.GetValue()

        if name == "":
            return

        if self.session.query(Preset).filter(Preset.name == name).count() != 0:
            dlg = wx.MessageDialog(self, 'The name "{0}" exists. Cannot add'.format(name),
                                   'Add Preset',
                                   wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            return

        new_preset = Preset(name=name)
        self.session.add(new_preset)
        self.session.flush()

        for row in self.patient_panel.patient.rxs:
            new_presetrx = PresetRx(preset_id=new_preset.id,
                                    drug_name=row.drug_name,
                                    drug_order=row.drug_order,
                                    active=row.active)
            self.session.add(new_presetrx)

        self.session.commit()


    def OnPresetMenu(self, event):
        """Add present prescreption"""
        preset_menu = wx.Menu()

        menu_id = 802
        for preset in self.session.query(Preset.name).order_by(Preset.name):
            preset_menu.Append(menu_id, preset.name)
            wx.EVT_MENU(self, menu_id, self.OnSelectPreset)
            menu_id += 1

        preset_menu.AppendSeparator()

        preset_menu.Append(800, "Add Current", "Add current prescription to presets.")
        wx.EVT_MENU(self, 800, self.OnAddPreset)

        remove_menu = wx.Menu()
        for preset in self.session.query(Preset.name).order_by(Preset.name):
            remove_menu.Append(menu_id, preset.name)
            wx.EVT_MENU(self, menu_id, self.OnRemovePreset)
            menu_id += 1

        preset_menu.AppendMenu(801, "Remove", remove_menu, "Remove prescription preset")

        event.GetEventObject().PopupMenu(preset_menu)
