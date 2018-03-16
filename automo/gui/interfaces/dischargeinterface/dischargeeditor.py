"""Admission Panel"""
import wx
import wx.lib.agw.labelbook

from .... import database as db
from .... import config

from ...clinicalencounterspanel.baseclinicalencounterpanel import BaseClinicalEncounterPanel
from ...encounternotebookform import EncounterNotebookForm
from ...vitalspanel import VitalsPanel
from ...measurementspanel import MeasurementsPanel
from ...subencounters import Subencounters
from ...prescriptionpanel import PrescriptionPanel
from ...problempanel import ProblemPanel
from ... import dbform as fm


class PatientNotebookForm(EncounterNotebookForm):
    def __init__(self, parent, session, **kwds):
        fields = [
            fm.StringField("Hospital No.", "hospital_no", required=True),
            fm.StringField("National Id No.", "national_id_no", required=True),
            fm.StringField("Name", "name", required=True),
            fm.DateTimeField("Date of Birth", "time_of_birth", required=True),
            fm.EnumField("Sex", "sex", ["M", "F"], required=True),
            fm.OptionalMultilineStringField("Known Allergies", "allergies", lines=3),
            fm.StringField("Phone No.", "phone_no"),
            fm.AddressField("Current Address", "current_address"),
            fm.AddressField("Permanent Address", "permanent_address")
        ]
        super(PatientNotebookForm, self).__init__(parent, session, db_encounter_class=db.Patient, fields=fields, **kwds)
        print self.form.db_object_class


    def save_changes(self):
        if self.encounter is not None:
            patient = self.encounter.patient
            self.form.update_object(patient)
            self.session.commit()
            self.changed = False
            self._update_toolbar()


    def set_encounter(self, encounter):
        self.encounter = encounter

        patient = None
        if self.encounter is not None:
            patient = self.encounter.patient

        self.form.set_object(patient)

        self.changed = False
        self._update_toolbar()




class DischargeEditor(BaseClinicalEncounterPanel):
    """Admission Panel"""
    def __init__(self, parent, session, **kwds):
        super(DischargeEditor, self).__init__(parent, session, **kwds)

        self.notebook = wx.lib.agw.labelbook.LabelBook(self, agwStyle=wx.lib.agw.labelbook.INB_BOLD_TAB_SELECTION)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._on_changing_notebook)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_change_notebook)

        self.create_notebook()

        self.notebook.SetSelection(1)

        self.sizer.Add(self.notebook, 1, wx.EXPAND)

    def create_notebook(self):
        self.patient_details_page = PatientNotebookForm(self.notebook, self.session)
        self.notebook.AddPage(self.patient_details_page, "Patient Details")
        
        fields = [
            fm.RelationField("Admitting Doctor", 'personnel', self.session.query(db.Doctor), required=True),
            fm.BedField("Bed", 'discharged_bed', self.session.query(db.Ward), required=True),
            fm.DateTimeField("Admission Time", 'start_time', required=True),
            fm.DateTimeField("Discharge Time", 'end_time', required=True)
        ]
        self.admission_details_page = EncounterNotebookForm(self.notebook, self.session, db.Admission, fields)
        self.notebook.AddPage(self.admission_details_page, "Admission Details")

        self.problems_panel = ProblemPanel(self.notebook, self.session)
        self.notebook.AddPage(self.problems_panel, "Diagnosis")

        fields = [
            fm.MultilineStringField("Cheif Complaints", 'chief_complaints', lines=4),
            fm.MultilineStringField("History of Present Illness", 'history', lines=8),
            fm.MultilineStringField("Past History", 'past_history', lines=8),
        ]
        self.history_page = EncounterNotebookForm(self.notebook, self.session, db.Admission, fields)
        self.notebook.AddPage(self.history_page, "History")

        self.vitals_panel = VitalsPanel(self.notebook, self.session)
        self.notebook.AddPage(self.vitals_panel, "Vital Signs")

        self.measurements_panel = MeasurementsPanel(self.notebook, self.session)
        self.notebook.AddPage(self.measurements_panel, "Measurements")

        fields = [
            fm.OptionalMultilineStringField("General Inspection", 'general_inspection', lines=8),
            fm.OptionalMultilineStringField("Head Exam", 'exam_head', lines=8),
            fm.OptionalMultilineStringField("Neck Exam", 'exam_neck', lines=8),
            fm.OptionalMultilineStringField("Chest Exam", 'exam_chest', lines=8),
            fm.OptionalMultilineStringField("Abdomen Exam", 'exam_abdomen', lines=8),
            fm.OptionalMultilineStringField("Genitalia Exam", 'exam_genitalia', lines=8),
            fm.OptionalMultilineStringField("Pelvic/Rectal Exam", 'exam_pelvic_rectal', lines=8),
            fm.OptionalMultilineStringField("Extremities Exam", 'exam_extremities', lines=8),
            fm.OptionalMultilineStringField("Other Exam", 'exam_other', lines=8)
        ]
        self.examination_page = EncounterNotebookForm(self.notebook, self.session, db.Admission, fields)
        self.notebook.AddPage(self.examination_page, "Examination")

        self.investigations_page = Subencounters(self.notebook, self.session)
        self.notebook.AddPage(self.investigations_page, "Investigations")

        imaging_fields = [
            fm.DateField("Date", 'record_time', required=True),
            fm.StringField("Imaging Type", 'imaging_type'),
            fm.StringField("Site", 'site'),
            fm.StringField("Radiologist", 'radiologist'),
            fm.MultilineStringField("Impression", 'impression'),
            fm.MultilineStringField("Report", 'report')
        ]
        self.investigations_page.add_subencounter_class("Imaging Report",
                                                  db.Imaging,
                                                  imaging_fields,
                                                  lambda v: u"{0} {1}".format(v.imaging_type, v.site))

        endoscopy_fields = [
            fm.DateField("Time", 'record_time', required=True),
            fm.StringField("Site", 'site'),
            fm.StringField("Endoscopist", 'endoscopist'),
            fm.MultilineStringField("Impression", 'impression'),
            fm.MultilineStringField("Report", 'report')
        ]
        self.investigations_page.add_subencounter_class("Endoscopy Report",
                                                  db.Endoscopy,
                                                  endoscopy_fields,
                                                  lambda v: u"{}".format(v.site))

        histopathology_fields = [
            fm.DateField("Time", 'record_time', required=True),
            fm.StringField("Site", 'site'),
            fm.StringField("Pathologist", 'pathologist'),
            fm.MultilineStringField("Impression", 'impression'),
            fm.MultilineStringField("Report", 'report')
        ]
        self.investigations_page.add_subencounter_class("Histopathology Report",
                                                  db.Histopathology,
                                                  histopathology_fields,
                                                  lambda v: u"{}".format(v.site))

        otherreport_fields = [
            fm.DateField("Time", 'record_time', required=True),
            fm.StringField("Name", 'name'),
            fm.StringField("Reported by", 'reported_by'),
            fm.MultilineStringField("Impression", 'impression'),
            fm.MultilineStringField("Report", 'report')
        ]
        self.investigations_page.add_subencounter_class("Other Report",
                                                  db.OtherReport,
                                                  otherreport_fields,
                                                  lambda v: u"{}".format(v.name))

        self.surgical_procedures_page = Subencounters(self.notebook, self.session)
        self.notebook.AddPage(self.surgical_procedures_page, "Surgical Procedures")

        fields = [
            fm.StringField("Procedure Name", 'procedure_name'),
            fm.CheckBoxField("Emergency", 'emergency'),
            fm.StringField("Preop Diagnosis", 'preoperative_diagnosis'),
            fm.StringField("Postop Diagnosis", 'postoperative_diagnosis'),
            fm.DateTimeField("Time Started", 'start_time', required=True),
            fm.DateTimeField("Time Completed", 'end_time', required=True),
            fm.RelationField("Surgeon", 'personnel', self.session.query(db.Doctor)),
            fm.StringField("Assistants(s)", 'assistant'),
            fm.StringField("Anesthetist(s)", 'anesthetist'),
            fm.StringField("Nurse(s)", 'nurse'),
            fm.MultilineStringField("Findings", 'findings'),
            fm.MultilineStringField("Steps", 'steps'),
        ]
        self.surgical_procedures_page.add_subencounter_class("Surgery",
                                                       db.SurgicalProcedure,
                                                       fields,
                                                       lambda v: u"&nbsp;{}".format(v.procedure_name))

        fields = [
            fm.MultilineStringField("", 'hospital_course', lines=8)
        ]
        self.course_page = EncounterNotebookForm(self.notebook, self.session, db.Admission, fields, scrollable=False)
        self.notebook.AddPage(self.course_page, "Hospital Course Summary")

        complication_fields = [
            fm.RelationField("Complication Grade",
                            'complication_grade',
                            self.session.query(db.ComplicationGrade),
                            help_text="\n\n".join(["Grade {0} - {1}".format(v.id, v.description) for v in self.session.query(db.ComplicationGrade).all()])),
            fm.CheckBoxField("Disability on Discharge", 'complication_disability'),
            fm.MultilineStringField("Complication Summary", 'complication_summary', lines=8)
        ]
        self.complication_panel = EncounterNotebookForm(self.notebook, self.session, db.Admission,
                                                          complication_fields)
        self.notebook.AddPage(self.complication_panel, "Complications")

        self.prescription_panel = PrescriptionPanel(self.notebook, self.session)
        self.notebook.AddPage(self.prescription_panel, "Prescription")

        fields = [
            fm.MultilineStringField("Advice", 'discharge_advice', lines=8),
            fm.MultilineStringField("Follow Up", 'follow_up', lines=8),
            fm.StringField("Discharge Prepared By", 'written_by', required=True)
        ]
        self.advice_page = EncounterNotebookForm(self.notebook, self.session, db.Admission, fields)
        self.notebook.AddPage(self.advice_page, "Discharge Advice")


    def _on_change_notebook(self, event):
        active_page = self.notebook.GetPage(event.GetSelection())
        active_page.set_encounter(self.encounter)
        active_page.set_editable(self.editable)


    def _on_changing_notebook(self, event):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page.is_unsaved():
            active_page.save_changes()
            print "Changes saved"
            #event.Veto() and return to cancel switch to new tab


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing"""
        if self.encounter is None:
            return False

        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page.is_unsaved():
            return True
        return False


    def save_changes(self):
        """Save changes"""
        if self.encounter is None:
            return

        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        active_page.save_changes()


    def set(self, encounter, *args, **kwds):
        if encounter is None:
            self.unset()
            return

        patient = encounter.patient

        super(DischargeEditor, self).set(encounter, *args, **kwds)
        
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        active_page.set_encounter(self.encounter)
        self.notebook.Show()
        
        self.info_panel.Hide()
        self.set_editable(True)


    def unset(self):
        super(DischargeEditor, self).unset()

        self.info_panel.Hide()
        self.notebook.Hide()
