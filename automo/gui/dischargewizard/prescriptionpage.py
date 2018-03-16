"""Prescription Page"""
from ... import database as db
from ..baseprescriptionpanel import BasePrescriptionPanel
from ..newadmissionwizard.basepage import BasePage


class PrescriptionPage(BasePrescriptionPanel, BasePage):
    """Prescription Page"""
    def __init__(self, parent, session, title, **kwds):
        super(PrescriptionPage, self).__init__(parent, session, title=title, **kwds)

        self.prescription = []


    def add_item(self, selected_drug, selected_drug_str, order_str, active=True):
        new_presc = db.ClinicalEncounter._create_new_prescription(db.ClinicalEncounter(), self.session, selected_drug, selected_drug_str, order_str, active)
        self.prescription.append(new_presc)


    def remove_item(self, item):
        self.prescription.remove(item)


    def get_prescription(self):
        return self.prescription


    def set_item_active(self, item, state=True):
        item.active = state


    def set_item_order(self, item, drug_order):
        item.drug_order = drug_order
