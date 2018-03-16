"""Select the patient, TODO: Handle Duplicate Patients"""
import wx

from ... import database as db
from ..patientsearchpanel import PatientSearchPanel
from ..patientinfo import PatientFormPanel
from .basepage import BasePage


class PatientSelectorPage(BasePage):
    """Select the patient, TODO: Handle Duplicate Patients"""
    def __init__(self, parent, session):
        super(PatientSelectorPage, self).__init__(parent, session, "Select Patient")

        self.new_patient = db.Patient()
        
        self.notebook = wx.Notebook(self)

        self.old_patient_panel = PatientSearchPanel(self.notebook, self.session)
        self.notebook.AddPage(self.old_patient_panel, "Existing Patient")
        self.sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, border=5)

        self.new_patient_panel = PatientFormPanel(self.notebook)
        self.notebook.AddPage(self.new_patient_panel, "New Patient")

    def is_valid(self):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page == self.new_patient_panel:
            invalid, lst_invalid = self.new_patient_panel.check()
            if invalid:
                self.error_message = "Following fields are not valid:\n\n{}".format("\n".join(lst_invalid))
                return False
            return True
        else:
            selected_patient = self.old_patient_panel.get_selected()
            if selected_patient is None:
                self.error_message = "No Patient Selected"
                return False
            current_encounter = selected_patient.get_current_encounter(self.session)
            if current_encounter is not None:
                self.error_message = "This patient already has an active encounter. Cannot admit before ending all active encounters."
                return False
            return True

    def get_patient(self):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page == self.new_patient_panel:
            self.new_patient_panel.update_object(self.new_patient)
            return self.new_patient
        else:
            return self.old_patient_panel.get_selected()
