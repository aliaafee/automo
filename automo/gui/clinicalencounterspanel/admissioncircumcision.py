"""Circumcision Admission Panel"""
import wx

from ... import database as db

from .admissionpanel import AdmissionPanel
from .. import dbform as fm
from ..pdfviewer import PDFViewer
from .. import encounternotebookpage as notepage
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
            fm.MultilineStringField("Chief Complaints", 'chief_complaints', lines=4),
            fm.OptionsField("Past History", 'past_history',options=['No significant past history'],
                           nonelabel="Unknown", otherlabel="Specify", lines=4),
            fm.OptionalMultilineStringField("Chest Exam", 'exam_chest', lines=4),
            fm.OptionalMultilineStringField("Abdomen Exam", 'exam_abdomen', lines=4),
            fm.OptionsField("Genital Exam", 'exam_genitalia',options=['Normal'],
                           nonelabel="Not Examined", otherlabel="Abnormal", lines=4),
            fm.OptionalMultilineStringField("Other Exam", 'exam_other', lines=4),
            fm.MultilineStringField("Preoperative Orders", 'preoperative_orders', lines=4)
        ]
        self.admission_note_panel = notepage.Form(self.notebook, self.session, db.Admission,
                                                          admission_note_fields)
        self.notebook.AddPage(self.admission_note_panel, "Admission Notes")

        self.vitals_panel = notepage.VitalsPanel(self.notebook, self.session)
        self.notebook.AddPage(self.vitals_panel, "Vitals")

        self.measurements_panel = notepage.MeasurementsPanel(self.notebook, self.session)
        self.notebook.AddPage(self.measurements_panel, "Measurements")

        self.subencounters = notepage.Subencounters(self.notebook, self.session)
        progress_fields = [
            fm.DateTimeField("Time", 'examination_time', required=True),
            fm.RelationField("Doctor", 'personnel', self.session.query(db.Doctor)),
            fm.MultilineStringField("Subjective", 'subjective'),
            fm.MultilineStringField("Objective", 'objective'),
            fm.MultilineStringField("Assessment", 'assessment'),
            fm.MultilineStringField("Plan", 'plan')
        ]
        self.subencounters.add_subencounter_class("Progress Note", db.Progress, progress_fields)

        procedure_fields = [
            fm.DateTimeField("Time Started", 'start_time', required=True),
            fm.DateTimeField("Time Completed", 'end_time', required=True),
            fm.RelationField("Surgeon", 'personnel', self.session.query(db.Doctor)),
            fm.StringField("Assistants(s)", 'assistant'),
            fm.StringField("Anesthetist(s)", 'anesthetist'),
            fm.StringField("Nurse(s)", 'nurse'),
            fm.StringField("Preop Diagnosis", 'preoperative_diagnosis'),
            fm.StringField("Postop Diagnosis", 'postoperative_diagnosis'),
            fm.StringField("Procedure Name", 'procedure_name'),
            fm.MultilineStringField("Findings", 'findings'),
            fm.MultilineStringField("Steps", 'steps'),
        ]
        self.subencounters.add_subencounter_class("Procedure Note", db.SurgicalProcedure, procedure_fields)

        imaging_fields = [
            fm.DateTimeField("Time", 'record_time', required=True),
            fm.StringField("Imaging Type", 'imaging_type'),
            fm.StringField("Site", 'site'),
            fm.StringField("Radiologist", 'radiologist'),
            fm.MultilineStringField("Impression", 'impression'),
            fm.MultilineStringField("Report", 'report')
        ]
        self.subencounters.add_subencounter_class("Imaging Report", db.Imaging, imaging_fields)

        endoscopy_fields = [
            fm.DateTimeField("Time", 'record_time', required=True),
            fm.StringField("Site", 'site'),
            fm.StringField("Endoscopist", 'endoscopist'),
            fm.MultilineStringField("Impression", 'impression'),
            fm.MultilineStringField("Report", 'report')
        ]
        self.subencounters.add_subencounter_class("Endoscopy Report", db.Endoscopy, endoscopy_fields)

        histopathology_fields = [
            fm.DateTimeField("Time", 'record_time', required=True),
            fm.StringField("Site", 'site'),
            fm.StringField("Pathologist", 'pathologist'),
            fm.MultilineStringField("Impression", 'impression'),
            fm.MultilineStringField("Report", 'report')
        ]
        self.subencounters.add_subencounter_class("Histopathology Report", db.Histopathology, histopathology_fields)
        
        other_fields = [
            fm.DateTimeField("Time Started", 'start_time', required=True),
            fm.DateTimeField("Time Completed", 'end_time', required=True),
            fm.MultilineStringField("Note", 'note')
        ]
        self.subencounters.add_subencounter_class("Other", db.OtherEncounter, other_fields)

        self.notebook.AddPage(self.subencounters, "Notes and Reports")

        complication_fields = [
            fm.RelationField("Complication Grade",
                            'complication_grade',
                            self.session.query(db.ComplicationGrade),
                            help_text="\n\n".join(["Grade {0} - {1}".format(v.id, v.description) for v in self.session.query(db.ComplicationGrade).all()])),
            fm.CheckBoxField("Disability on Discharge", 'complication_disability'),
            fm.MultilineStringField("Complication Summary", 'complication_summary', lines=8)
        ]
        self.complication_panel = notepage.Form(self.notebook, self.session, db.Admission,
                                                          complication_fields)
        self.notebook.AddPage(self.complication_panel, "Complications")

        discharge_note_fields = [
            fm.OptionsField("Hospital Course", 'hospital_course',options=['Uneventful'],
                           nonelabel="Unspecified", otherlabel="Issues", lines=4),
            fm.MultilineStringField("Discharge Advice", 'discharge_advice', lines=4),
            fm.MultilineStringField("Follow Up", 'follow_up', lines=4)
        ]
        self.discharge_note_panel = notepage.Form(self.notebook, self.session, db.Admission,
                                                          discharge_note_fields)
        self.notebook.AddPage(self.discharge_note_panel, "Discharge Notes")

        self.prescription_panel = notepage.PrescriptionPanel(self.notebook, self.session)
        self.notebook.AddPage(self.prescription_panel, "Prescription")
