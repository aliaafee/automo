"""Discharge Wizard"""
import datetime
import wx
import wx.adv

from .. import database as db
from .dbform import DbFormPanel,\
                    DbDateTimeField,\
                    DbRelationField,\
                    DbMultilineStringField,\
                    DbOptionalMultilineStringField,\
                    DbFloatField,\
                    DbCheckBoxField,\
                    DbOptionsRelationField
from .newadmission import BasePage
from .newadmission import PatientSelectorPage
from .newadmission import DoctorBedSelectorPage
from .newadmission import ProblemSelectorPage


class FormPage(BasePage):
    """Form Page"""
    def __init__(self, parent, session, title, db_object_class, fields, scrollable=True):
        super(FormPage, self).__init__(parent, session, title)

        self.form_panel = DbFormPanel(self, db_object_class, fields, scrollable)
        self.sizer.Add(self.form_panel, 1, wx.ALL | wx.EXPAND, border=5)


    def is_valid(self):
        blanks, lst_blanks = self.form_panel.check()
        if blanks:
            self.error_message = "These fields cannot be empty\n\n{}".format("\n".join(lst_blanks))
            return False
        return True


    def set_object(self, db_object):
        self.form_panel.set_object(db_object)


    def update_db_object(self, db_object):
        self.form_panel.update_object(db_object)
    


class ComplicationsPage(FormPage):
    """Complications Page"""
    def __init__(self, parent, session):
        fields = [
            DbOptionsRelationField("Complication Grade",
                                   'complication_grade',
                                   session.query(db.ComplicationGrade),
                                   value_formatter=lambda v:"Grade {0} - {1}".format(v.id, v.description),
                                   required=True),
            DbCheckBoxField("Disability on Discharge", 'complication_disability'),
            DbMultilineStringField("Complication Summary", 'complication_summary', lines=8)
        ]
        super(ComplicationsPage, self).__init__(parent, session, 
            "Surgical Complication Grade", db.Admission, fields)


    def must_skip(self):
        if not self.Parent.get_surgical_procedures():
            return True
        return False




class DischargeWizard(wx.adv.Wizard):
    """Discharge Wizard"""
    def __init__(self, parent, session, **kwds):
        super(DischargeWizard, self).__init__(
            parent,
            style=wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION,
            **kwds)

        default_admission = db.Admission(
            start_time = datetime.datetime.now(),
            end_time = datetime.datetime.now(),
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
            DbRelationField("Admitting Doctor", 'personnel', self.session.query(db.Doctor), required=True),
            DbDateTimeField("Admission Time", 'start_time', required=True),
            DbDateTimeField("Discharge Time", 'end_time', required=True),
            DbRelationField("Bed", 'discharged_bed', self.session.query(db.Bed), required=True)
        ]
        self.admission_details = FormPage(self, session, "Admission Details", db.Admission, fields)
        self.add_page(self.admission_details)

        self.problem_selector = ProblemSelectorPage(self, session)
        self.add_page(self.problem_selector)

        fields = [
            DbMultilineStringField("Cheif Complaints", 'chief_complaints', lines=4),
            DbMultilineStringField("History of Present Illness", 'history', lines=8),
            DbMultilineStringField("Past History", 'past_history', lines=8),
        ]
        self.history = FormPage(self, session, "History", db.Admission, fields)
        self.add_page(self.history)

        fields = [
            DbDateTimeField("Time", 'record_time'),
            DbFloatField("Pulse (bmp)", 'pulse_rate'),
            DbFloatField("Resp (bmp)", 'respiratory_rate'),
            DbFloatField("SBP (mmHg)", 'systolic_bp'),
            DbFloatField("DBP (mmHg)", 'diastolic_bp'),
            DbFloatField(u"Temp (\u00B0C)", 'temperature')
        ]
        self.vitals_page = FormPage(self, session, "Vital Signs", db.VitalSigns, fields)
        self.add_page(self.vitals_page)

        fields = [
            DbDateTimeField("Time", 'record_time'),
            DbFloatField("Weight (kg)", 'weight'),
            DbFloatField("Height (m)", 'height')
        ]
        self.measurements_page = FormPage(self, session, "Measurements", db.Measurements, fields)
        self.add_page(self.measurements_page)

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
        self.examination = FormPage(self, session, "Examination", db.Admission, fields)
        self.add_page(self.examination)

        self.investigations = BasePage(self, session, "Investigations & Reports")
        self.add_page(self.investigations)

        self.surgical_procedures = BasePage(self, session, "Operations")
        self.add_page(self.surgical_procedures)

        fields = [
            DbMultilineStringField("", 'hospital_course', lines=8)
        ]
        self.course = FormPage(self, session, "Hospital Course Summary", db.Admission, fields, False)
        self.add_page(self.course)

        
        self.complication = ComplicationsPage(self, session) #FormPage(self, session, "Surgical Complication Grade", db.ComplicationGrade, fields)
        self.add_page(self.complication)

        self.prescription = BasePage(self, session, "Prescription")
        self.add_page(self.prescription)

        fields = [
            DbMultilineStringField("Advice", 'discharge_advice', lines=8),
            DbMultilineStringField("Follow Up", 'follow_up', lines=8)
        ]
        self.advice = FormPage(self, session, "Discharge Advice", db.Admission, fields)
        self.add_page(self.advice)

        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self._on_page_changing)
        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self._on_page_changed)
        self.Bind(wx.adv.EVT_WIZARD_FINISHED, self._on_finish)

        self.admission_pages = [
            self.admission_details,
            self.history,
            self.examination,
            self.course,
            self.complication,
            self.advice
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
        if vitals.record_time is not None:
            admission.add_child_encounter(vitals)

        measurements = db.VitalSigns()
        self.measurements_page.update_db_object(measurements)
        if measurements.record_time is not None:
            admission.add_child_encounter(measurements)

        problems = self.get_problems()
        for problem in problems:
            if problem not in admission.patient.problems:
                admission.patient.problems.append(problem)
            admission.problems.append(problem)

        #TODO Add the investigations subencounters

        #TODO Add the procedure sub_encounters

        #TODO Add Prescription

        return admission


    def get_surgical_procedures(self):
        procedures = ["a","b"]
        return procedures


    def get_bed(self):
        return self.doctorbed_selector.get_bed()


    def get_doctor(self):
        return self.doctorbed_selector.get_doctor()


    def get_problems(self):
        return self.problem_selector.get_problems()


    def _on_page_changing(self, event):
        if event.GetDirection():#Going Forward
            page = event.GetPage()
            if not page.is_valid():
                page.show_error()
                event.Veto()


    def _on_page_changed(self, event):
        page = event.GetPage()
        page.set()
        if page.must_skip():
            current_index = self.pages.index(page)
            if current_index < len(self.pages) - 1:
                next_page = self.pages[current_index + 1]
                self.ShowPage(next_page)


    def _on_finish(self, event):
        self.SetReturnCode(wx.ID_OK)