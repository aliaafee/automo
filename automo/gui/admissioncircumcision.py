"""Circumcision Admission Panel"""
import wx

from .. import database as db

from .admissionpanel import AdmissionPanel
from .measurementspanel import MeasurementsPanel
from .vitalspanel import VitalsPanel
from .prescriptionpanel import PrescriptionPanel
from .surgerypanel import SurgeryPanel
from .encounternotebookform import EncounterNotebookForm
from .dbform import DbMultilineStringField,\
                    DbOptionalMultilineStringField,\
                    DbOptionsField
from .pdfviewer import PDFViewer

ID_PRINT_ADMISSION = wx.NewId()


class AdmissionCircumcisionPanel(AdmissionPanel):
    """Circumcision Admission Panel"""
    def __init__(self, parent, session, **kwds):
        super(AdmissionCircumcisionPanel, self).__init__(parent, session, **kwds)
        
        self.set_title("Circumcision")

        self.encounter_type = "circumcisionadmission"


    def create_print_menu(self):
        #self.print_menu.Append(ID_PRINT_ADMISSION, "Admission Summary", "Print Admission Summary")
        #self.print_menu.Bind(wx.EVT_MENU, self._on_print_admission, id=ID_PRINT_ADMISSION)
        
        super(AdmissionCircumcisionPanel, self).create_print_menu()


    def _on_print_admission(self, event):
        pass


    def create_notebook(self):
        print "Creating it"
        admission_note_fields = [
            DbMultilineStringField("Chief Complaints", 'chief_complaints', lines=4),
            DbOptionsField("Past History", 'past_history',options=['No significant past history'],
                           nonelabel="Unknown", otherlabel="Specify", lines=8),
            DbOptionalMultilineStringField("Chest Exam", 'exam_chest', lines=8),
            DbOptionalMultilineStringField("Abdomen Exam", 'exam_abdomen', lines=8),
            DbOptionsField("Genital Exam", 'exam_genitalia',options=['Normal'],
                           nonelabel="Not Examined", otherlabel="Abnormal", lines=4),
            DbOptionalMultilineStringField("Other Exam", 'exam_other', lines=8),
            DbOptionsField("Hospital Course", 'hospital_course',options=['Uneventful'],
                           nonelabel="Unspecified", otherlabel="Issues", lines=4),
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
