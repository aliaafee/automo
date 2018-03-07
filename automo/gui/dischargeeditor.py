"""Admission Panel"""
import wx
import wx.lib.agw.labelbook

from .. import database as db
from .. import config
from .baseclinicalencounterpanel import BaseClinicalEncounterPanel
from .encounternotebookform import EncounterNotebookForm
from .vitalspanel import VitalsPanel
from .measurementspanel import MeasurementsPanel
from .subencounters import Subencounters
from .prescriptionpanel import PrescriptionPanel
from .problempanel import ProblemPanel
from .dbform import DbFormPanel,\
                    DbDateTimeField,\
                    DbRelationField,\
                    DbMultilineStringField,\
                    DbOptionalMultilineStringField,\
                    DbFloatField,\
                    DbCheckBoxField,\
                    DbStringField,\
                    DbOptionsRelationField,\
                    DbFormSwitcher,\
                    DbBedField,\
                    DbDateField,\
                    DbDurationField,\
                    DbEnumField,\
                    DbAddressField





class PatientNotebookForm(EncounterNotebookForm):
    def __init__(self, parent, session, **kwds):
        fields = [
            DbStringField("Hospital No.", "hospital_no", required=True),
            DbStringField("National Id No.", "national_id_no", required=True),
            DbStringField("Name", "name", required=True),
            DbDateTimeField("Date of Birth", "time_of_birth", required=True),
            DbEnumField("Sex", "sex", ["M", "F"], required=True),
            DbOptionalMultilineStringField("Known Allergies", "allergies", lines=3),
            DbStringField("Phone No.", "phone_no"),
            DbAddressField("Current Address", "current_address"),
            DbAddressField("Permanent Address", "permanent_address")
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

        self.sizer.Add(self.notebook, 1, wx.EXPAND)

    def create_notebook(self):
        self.patient_details_page = PatientNotebookForm(self.notebook, self.session)
        self.notebook.AddPage(self.patient_details_page, "Patient Details")
        
        fields = [
            DbRelationField("Admitting Doctor", 'personnel', self.session.query(db.Doctor), required=True),
            DbBedField("Bed", 'discharged_bed', self.session.query(db.Ward), required=True),
            DbDateTimeField("Admission Time", 'start_time', required=True),
            DbDateTimeField("Discharge Time", 'end_time', required=True)
        ]
        self.admission_details_page = EncounterNotebookForm(self.notebook, self.session, db.Admission, fields)
        self.notebook.AddPage(self.admission_details_page, "Admission Details")

        self.problems_panel = ProblemPanel(self.notebook, self.session)
        self.notebook.AddPage(self.problems_panel, "Diagnosis")

        fields = [
            DbMultilineStringField("Cheif Complaints", 'chief_complaints', lines=4),
            DbMultilineStringField("History of Present Illness", 'history', lines=8),
            DbMultilineStringField("Past History", 'past_history', lines=8),
        ]
        self.history_page = EncounterNotebookForm(self.notebook, self.session, db.Admission, fields)
        self.notebook.AddPage(self.history_page, "History")

        self.vitals_panel = VitalsPanel(self.notebook, self.session)
        self.notebook.AddPage(self.vitals_panel, "Vital Signs")

        self.measurements_panel = MeasurementsPanel(self.notebook, self.session)
        self.notebook.AddPage(self.measurements_panel, "Measurements")

        fields = [
            DbOptionalMultilineStringField("General Inspection", 'general_inspection', lines=8),
            DbOptionalMultilineStringField("Head Exam", 'exam_head', lines=8),
            DbOptionalMultilineStringField("Neck Exam", 'exam_neck', lines=8),
            DbOptionalMultilineStringField("Chest Exam", 'exam_chest', lines=8),
            DbOptionalMultilineStringField("Abdomen Exam", 'exam_abdomen', lines=8),
            DbOptionalMultilineStringField("Genitalia Exam", 'exam_genitalia', lines=8),
            DbOptionalMultilineStringField("Pelvic/Rectal Exam", 'exam_pelvic_rectal', lines=8),
            DbOptionalMultilineStringField("Extremities Exam", 'exam_extremities', lines=8),
            DbOptionalMultilineStringField("Other Exam", 'exam_other', lines=8)
        ]
        self.examination_page = EncounterNotebookForm(self.notebook, self.session, db.Admission, fields)
        self.notebook.AddPage(self.examination_page, "Examination")

        self.investigations_page = Subencounters(self.notebook, self.session)
        self.notebook.AddPage(self.investigations_page, "Investigations")

        imaging_fields = [
            DbDateField("Date", 'record_time', required=True),
            DbStringField("Imaging Type", 'imaging_type'),
            DbStringField("Site", 'site'),
            DbStringField("Radiologist", 'radiologist'),
            DbMultilineStringField("Impression", 'impression'),
            DbMultilineStringField("Report", 'report')
        ]
        self.investigations_page.add_subencounter_class("Imaging Report",
                                                  db.Imaging,
                                                  imaging_fields,
                                                  lambda v: u"{0} {1}".format(v.imaging_type, v.site))

        endoscopy_fields = [
            DbDateField("Time", 'record_time', required=True),
            DbStringField("Site", 'site'),
            DbStringField("Endoscopist", 'endoscopist'),
            DbMultilineStringField("Impression", 'impression'),
            DbMultilineStringField("Report", 'report')
        ]
        self.investigations_page.add_subencounter_class("Endoscopy Report",
                                                  db.Endoscopy,
                                                  endoscopy_fields,
                                                  lambda v: u"{}".format(v.site))

        histopathology_fields = [
            DbDateField("Time", 'record_time', required=True),
            DbStringField("Site", 'site'),
            DbStringField("Pathologist", 'pathologist'),
            DbMultilineStringField("Impression", 'impression'),
            DbMultilineStringField("Report", 'report')
        ]
        self.investigations_page.add_subencounter_class("Histopathology Report",
                                                  db.Histopathology,
                                                  histopathology_fields,
                                                  lambda v: u"{}".format(v.site))

        otherreport_fields = [
            DbDateField("Time", 'record_time', required=True),
            DbStringField("Name", 'name'),
            DbStringField("Reported by", 'reported_by'),
            DbMultilineStringField("Impression", 'impression'),
            DbMultilineStringField("Report", 'report')
        ]
        self.investigations_page.add_subencounter_class("Other Report",
                                                  db.OtherReport,
                                                  otherreport_fields,
                                                  lambda v: u"{}".format(v.name))

        self.surgical_procedures_page = Subencounters(self.notebook, self.session)
        self.notebook.AddPage(self.surgical_procedures_page, "Surgical Procedures")

        fields = [
            DbStringField("Procedure Name", 'procedure_name'),
            DbCheckBoxField("Emergency", 'emergency'),
            DbStringField("Preop Diagnosis", 'preoperative_diagnosis'),
            DbStringField("Postop Diagnosis", 'postoperative_diagnosis'),
            DbDateTimeField("Time Started", 'start_time', required=True),
            DbDateTimeField("Time Completed", 'end_time', required=True),
            DbRelationField("Surgeon", 'personnel', self.session.query(db.Doctor)),
            DbStringField("Assistants(s)", 'assistant'),
            DbStringField("Anesthetist(s)", 'anesthetist'),
            DbStringField("Nurse(s)", 'nurse'),
            DbMultilineStringField("Findings", 'findings'),
            DbMultilineStringField("Steps", 'steps'),
        ]
        self.surgical_procedures_page.add_subencounter_class("Surgery",
                                                       db.SurgicalProcedure,
                                                       fields,
                                                       lambda v: u"&nbsp;{}".format(v.procedure_name))

        fields = [
            DbMultilineStringField("", 'hospital_course', lines=8)
        ]
        self.course_page = EncounterNotebookForm(self.notebook, self.session, db.Admission, fields, scrollable=False)
        self.notebook.AddPage(self.course_page, "Hospital Course Summary")

        complication_fields = [
            DbRelationField("Complication Grade",
                            'complication_grade',
                            self.session.query(db.ComplicationGrade),
                            help_text="\n\n".join(["Grade {0} - {1}".format(v.id, v.description) for v in self.session.query(db.ComplicationGrade).all()])),
            DbCheckBoxField("Disability on Discharge", 'complication_disability'),
            DbMultilineStringField("Complication Summary", 'complication_summary', lines=8)
        ]
        self.complication_panel = EncounterNotebookForm(self.notebook, self.session, db.Admission,
                                                          complication_fields)
        self.notebook.AddPage(self.complication_panel, "Complications")

        self.prescription_panel = PrescriptionPanel(self.notebook, self.session)
        self.notebook.AddPage(self.prescription_panel, "Prescription")

        fields = [
            DbMultilineStringField("Advice", 'discharge_advice', lines=8),
            DbMultilineStringField("Follow Up", 'follow_up', lines=8),
            DbStringField("Discharge Prepared By", 'written_by', required=True)
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
