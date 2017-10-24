"""Circumcision Admission Panel"""
import wx

from .. import database as db

from .admissionpanel import AdmissionPanel
from .measurementspanel import MeasurementsPanel
from .vitalspanel import VitalsPanel
from .prescriptionpanel import PrescriptionPanel
from .surgerypanel import SurgeryPanel
from .encounternotebookform import EncounterNotebookForm
from .dbform import DbMultilineStringField
from .pdfviewer import PDFViewer

ID_PRINT_ADMISSION = wx.NewId()


class AdmissionCircumcisionPanel(AdmissionPanel):
    """Circumcision Admission Panel"""
    def __init__(self, parent, session, **kwds):
        super(AdmissionCircumcisionPanel, self).__init__(parent, session, **kwds)
        
        self.set_title("Circumcision")

        self.encounter_type = "circumcisionadmission"


    def create_print_menu(self):
        self.print_menu.Append(ID_PRINT_ADMISSION, "Admission Summary", "Print Admission Summary")
        self.print_menu.Bind(wx.EVT_MENU, self._on_print_admission, id=ID_PRINT_ADMISSION)
        
        super(AdmissionCircumcisionPanel, self).create_print_menu()


    def _on_print_admission(self, event):
        pass


    def create_notebook(self):
        print "Creating it"
        admission_note_fields = [
            DbMultilineStringField("History", 'history', lines=8),
            DbMultilineStringField("Examination", 'examination', lines=8),
            DbMultilineStringField("Hospital Course Summary", 'hospital_course', lines=8),
            DbMultilineStringField("Discharge Advice", 'discharge_advice', lines=8),
            DbMultilineStringField("Follow Up", 'follow_up', lines=8)
        ]
        self.admission_note_panel = EncounterNotebookForm(self.notebook, self.session, db.Admission,
                                                          admission_note_fields)
        self.notebook.AddPage(self.admission_note_panel, "Notes")

        self.surgery_panel = SurgeryPanel(self.notebook, self.session)
        self.notebook.AddPage(self.surgery_panel, "Procedures")

        self.measurements_panel = MeasurementsPanel(self.notebook, self.session)
        self.notebook.AddPage(self.measurements_panel, "Measurements")

        self.vitals_panel = VitalsPanel(self.notebook, self.session)
        self.notebook.AddPage(self.vitals_panel, "Vitals")

        self.prescription_panel = PrescriptionPanel(self.notebook, self.session)
        self.notebook.AddPage(self.prescription_panel, "Prescription")
