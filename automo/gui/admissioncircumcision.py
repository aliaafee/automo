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
ID_PRINT_OT_NOTE = wx.NewId()


class AdmissionCircumcisionPanel(AdmissionPanel):
    """Circumcision Admission Panel"""
    def __init__(self, parent, session, **kwds):
        super(AdmissionCircumcisionPanel, self).__init__(parent, session, **kwds)
        
        self.set_title("Circumcision")

        self.encounter_type = "circumcisionadmission"


    def create_print_menu(self):
        self.print_menu.Append(ID_PRINT_ADMISSION, "Admission Sheet", "Print Admission Sheet")
        self.print_menu.Bind(wx.EVT_MENU, self._on_print_admission, id=ID_PRINT_ADMISSION)

        self.print_menu.Append(ID_PRINT_OT_NOTE, "OT Note Template", "Print OT Note Template")
        self.print_menu.Bind(wx.EVT_MENU, self._on_print_ot_note, id=ID_PRINT_OT_NOTE)
        
        super(AdmissionCircumcisionPanel, self).create_print_menu()


    def _on_print_ot_note(self, event):
        filename = self.encounter.generate_ot_note(self.session)

        pdf_view = PDFViewer(None, title="Print Preview - OT Note Template")
        pdf_view.viewer.UsePrintDirect = ``False``
        pdf_view.viewer.LoadFile(filename)
        pdf_view.Show()


    def _on_print_admission(self, event):
        filename = self.encounter.generate_admission_summary(self.session)

        pdf_view = PDFViewer(None, title="Print Preview - Circumcision Admission Sheet")
        pdf_view.viewer.UsePrintDirect = ``False``
        pdf_view.viewer.LoadFile(filename)
        pdf_view.Show()


    def create_notebook(self):
        print "Creating it"
        admission_note_fields = [
            DbMultilineStringField("Chief Complaints", 'chief_complaints', lines=4),
            DbOptionsField("Past History", 'past_history',options=['No significant past history'],
                           nonelabel="Unknown", otherlabel="Specify", lines=4),
            DbOptionalMultilineStringField("Chest Exam", 'exam_chest', lines=4),
            DbOptionalMultilineStringField("Abdomen Exam", 'exam_abdomen', lines=4),
            DbOptionsField("Genital Exam", 'exam_genitalia',options=['Normal'],
                           nonelabel="Not Examined", otherlabel="Abnormal", lines=4),
            DbOptionalMultilineStringField("Other Exam", 'exam_other', lines=4),
            DbMultilineStringField("Preoperative Orders", 'preoperative_orders', lines=4)
        ]
        self.admission_note_panel = EncounterNotebookForm(self.notebook, self.session, db.Admission,
                                                          admission_note_fields)
        self.notebook.AddPage(self.admission_note_panel, "Admission Notes")

        self.vitals_panel = VitalsPanel(self.notebook, self.session)
        self.notebook.AddPage(self.vitals_panel, "Vitals")

        self.measurements_panel = MeasurementsPanel(self.notebook, self.session)
        self.notebook.AddPage(self.measurements_panel, "Measurements")

        self.surgery_panel = SurgeryPanel(self.notebook, self.session)
        self.notebook.AddPage(self.surgery_panel, "Procedures")

        discharge_note_fields = [
            DbOptionsField("Hospital Course", 'hospital_course',options=['Uneventful'],
                           nonelabel="Unspecified", otherlabel="Issues", lines=4),
            DbMultilineStringField("Discharge Advice", 'discharge_advice', lines=4),
            DbMultilineStringField("Follow Up", 'follow_up', lines=4)
        ]
        self.discharge_note_panel = EncounterNotebookForm(self.notebook, self.session, db.Admission,
                                                          discharge_note_fields)
        self.notebook.AddPage(self.discharge_note_panel, "Discharge Notes")

        self.prescription_panel = PrescriptionPanel(self.notebook, self.session)
        self.notebook.AddPage(self.prescription_panel, "Prescription")
