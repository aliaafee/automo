"""Prescription Panel"""
import wx
from ObjectListView import ColumnDefn

from ..baseprescriptionpanel import BasePrescriptionPanel
from .encounternotebookpage import EncounterNotebookPage


ID_PRESET_ADD = wx.NewId()
ID_PRESET_REMOVE = wx.NewId()

class PrescriptionPanel(BasePrescriptionPanel, EncounterNotebookPage):
    def __init__(self, parent, session, **kwds):
        super(PrescriptionPanel, self).__init__(parent, session, toolbar=True, **kwds)

        self.toolbar.Realize()
        self.toolbar.Show()

        self.editable_on()


    def _on_prescription_check(self, event):
        super(PrescriptionPanel, self)._on_prescription_check(event)
        self.session.commit()


    def _on_prescription_order_edit(self, event):
        super(PrescriptionPanel, self)._on_prescription_order_edit(event)
        self.session.commit()
    
    def add_item(self, selected_drug, selected_drug_str, order_str, active=True):
        self.encounter.prescribe_drug(self.session, selected_drug, selected_drug_str, order_str, active)
        self.session.commit()


    def remove_item(self, item):
        self.session.delete(item)
        self.session.commit()


    def get_prescription(self):
        if self.encounter is None:
            return []
        return self.encounter.prescription


    def set_item_active(self, item, state=True):
        item.active = state
        self.session.commit()


    def set_item_order(self, item, drug_order):
        item.drug_order = drug_order 


    def set_encounter(self, encounter, editable=True):
        EncounterNotebookPage(self, encounter)
        self.encounter = encounter
        self._refresh_prescription()

    
    def editable_on(self):
        self.drug_add_panel.Show()
        self.prescription_list.SetColumns([
            ColumnDefn("Medication", "left", 180, "drug", isEditable=False),
            ColumnDefn("Order", "left", 140, "drug_order")
        ])
        self.prescription_list.CreateCheckStateColumn()
        self._refresh_prescription()


    def editable_off(self):
        self.drug_add_panel.Hide()
        self.prescription_list.SetColumns([
            ColumnDefn("Medication", "left", 180, "drug", isEditable=False),
            ColumnDefn("Order", "left", 140, "drug_order", isEditable=False)
        ])
        self._refresh_prescription()
