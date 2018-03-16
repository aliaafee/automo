"""Discharge Wizard"""
from datetime import datetime
import wx

from ... import database as db
from ..newadmissionwizard.patientselectorpage import PatientSelectorPage
from ..newadmissionwizard.problemselectorpage import ProblemSelectorPage
from .. import dbform as fm
from .subencounterspage import SubencountersPage
from .complicationspage import ComplicationsPage
from .prescriptionpage import PrescriptionPage
from .formpage import FormPage


class DischargeWizard(wx.adv.Wizard):
    """Discharge Wizard"""
    def __init__(self, parent, session, **kwds):
        super(DischargeWizard, self).__init__(
            parent,
            style=wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION,
            **kwds)

        default_admission = db.Admission(
            start_time = datetime.now(),
            end_time = datetime.now(),
            complication_disability = False
        )

        self.SetTitle("New Discharge")

        self.SetPageSize((600, 500))

        self.pages = []

        self.session = session
        self.patient = None

        self.patient_selector = PatientSelectorPage(self, session)
        self.add_page(self.patient_selector)

        fields = [
            fm.RelationField("Admitting Doctor", 'personnel', self.session.query(db.Doctor), required=True),
            fm.BedField("Bed", 'discharged_bed', self.session.query(db.Ward), required=True),
            fm.DateTimeField("Admission Time", 'start_time', required=True),
            fm.DateTimeField("Discharge Time", 'end_time', required=True)
        ]
        self.admission_details_page = FormPage(self, session, "Admission Details", db.Admission, fields)
        self.add_page(self.admission_details_page)

        self.problem_selector = ProblemSelectorPage(self, session)
        self.add_page(self.problem_selector)

        fields = [
            fm.MultilineStringField("Cheif Complaints", 'chief_complaints', lines=4),
            fm.MultilineStringField("History of Present Illness", 'history', lines=8),
            fm.MultilineStringField("Past History", 'past_history', lines=8),
        ]
        self.history_page = FormPage(self, session, "History", db.Admission, fields)
        self.add_page(self.history_page)

        fields = [
            fm.FloatField("Pulse (bmp)", 'pulse_rate'),
            fm.FloatField("Resp (bmp)", 'respiratory_rate'),
            fm.FloatField("SBP (mmHg)", 'systolic_bp'),
            fm.FloatField("DBP (mmHg)", 'diastolic_bp'),
            fm.FloatField(u"Temp (\u00B0C)", 'temperature')
        ]
        self.vitals_page = FormPage(self, session, "Vital Signs", db.VitalSigns, fields)
        self.add_page(self.vitals_page)

        fields = [
            fm.FloatField("Weight (kg)", 'weight'),
            fm.FloatField("Height (m)", 'height')
        ]
        self.measurements_page = FormPage(self, session, "Measurements", db.Measurements, fields)
        self.add_page(self.measurements_page)

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
        self.examination_page = FormPage(self, session, "Examination", db.Admission, fields)
        self.add_page(self.examination_page)

        self.investigations_page = SubencountersPage(self, session, "Investigations && Reports")
        self.add_page(self.investigations_page)

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

        self.surgical_procedures_page = SubencountersPage(self, session, "Surgical Procedures")
        self.add_page(self.surgical_procedures_page)
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
        self.course_page = FormPage(self, session, "Hospital Course Summary", db.Admission, fields, False)
        self.add_page(self.course_page)

        
        self.complication_page = ComplicationsPage(self, session) #FormPage(self, session, "Surgical Complication Grade", db.ComplicationGrade, fields)
        self.add_page(self.complication_page)

        self.prescription_page = PrescriptionPage(self, session, "Prescription")
        self.add_page(self.prescription_page)

        fields = [
            fm.MultilineStringField("Advice", 'discharge_advice', lines=8),
            fm.MultilineStringField("Follow Up", 'follow_up', lines=8),
            fm.StringField("Discharge Prepared By", 'written_by', required=True)
        ]
        self.advice_page = FormPage(self, session, "Discharge Advice", db.Admission, fields)
        self.add_page(self.advice_page)

        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self._on_page_changing)
        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self._on_page_changed)
        self.Bind(wx.adv.EVT_WIZARD_FINISHED, self._on_finish)

        self.admission_pages = [
            self.admission_details_page,
            self.history_page,
            self.examination_page,
            self.course_page,
            self.complication_page,
            self.advice_page
        ]

        for page in self.admission_pages:
            page.set_object(default_admission)


    def add_page(self, page):
        if self.pages:
            previous_page = self.pages[-1]
            page.SetPrev(previous_page)
            previous_page.SetNext(page)
        self.pages.append(page)


    def ShowModal(self):
        self.RunWizard(self.pages[0])


    def get_patient(self):
        return self.patient_selector.get_patient()


    def get_admission(self):
        admission = db.Admission()
        admission.patient = self.get_patient()

        for page in self.admission_pages:
            page.update_db_object(admission)

        vitals = db.VitalSigns()
        self.vitals_page.update_db_object(vitals)
        if any([vitals.pulse_rate, vitals.respiratory_rate, vitals.diastolic_bp, vitals.systolic_bp, vitals.temperature]):
            vitals.record_time = admission.start_time
            admission.add_child_encounter(vitals)

        measurements = db.Measurements()
        self.measurements_page.update_db_object(measurements)
        if any([measurements.weight, measurements.height]):
            measurements.record_time = admission.start_time
            admission.add_child_encounter(measurements)

        problems = self.get_problems()
        for problem in problems:
            if problem not in admission.patient.problems:
                admission.patient.problems.append(problem)
            admission.problems.append(problem)

        investigations = self.get_investigations()
        for investigation in investigations:
            admission.add_child_encounter(investigation)

        procedures = self.get_surgical_procedures()
        for procedure in procedures:
            admission.add_child_encounter(procedure)

        prescription = self.get_prescription()
        for item in prescription:
            admission.prescription.append(item)

        return admission

    
    def get_prescription(self):
        return self.prescription_page.get_prescription()


    def get_surgical_procedures(self):
        return self.surgical_procedures_page.get_subencounters()


    def get_investigations(self):
        return self.investigations_page.get_subencounters()


    def get_bed(self):
        return self.doctorbed_selector.get_bed()


    def get_doctor(self):
        return self.doctorbed_selector.get_doctor()


    def get_problems(self):
        return self.problem_selector.get_problems()


    def _on_page_changing(self, event):
        if event.GetDirection():#Going Forward
            page = event.GetPage()
            if not page.must_skip():
                if not page.is_valid():
                    page.show_error()
                    event.Veto()


    def _on_page_changed(self, event):
        page = event.GetPage()
        page.set()
        if page.must_skip():
            current_index = self.pages.index(page)
            if event.GetDirection():#Going Forward
                if current_index < len(self.pages) - 1:
                    next_page = self.pages[current_index + 1]
                    self.ShowPage(next_page)
            else:#Goind Backward
                if current_index > 0:
                    next_page = self.pages[current_index - 1]
                    self.ShowPage(next_page)


    def _on_finish(self, event):
        self.SetReturnCode(wx.ID_OK)
