"""Discharge Wizard"""
from datetime import datetime
import wx
import wx.adv
from ObjectListView import ObjectListView, ColumnDefn, OLVEvent

from .. import database as db
from .. import config
from . import images
from . import events
from .dbform import DbFormPanel,\
                    DbDateTimeField,\
                    DbRelationField,\
                    DbMultilineStringField,\
                    DbOptionalMultilineStringField,\
                    DbFloatField,\
                    DbCheckBoxField,\
                    DbStringField,\
                    DbOptionsRelationField,\
                    DbFormSwitcher
from .dblistbox import DbListBox
from .acdbtextctrl import AcDbTextCtrl
from .objectlistviewmod import ObjectListViewMod, EVT_OVL_CHECK_EVENT
from .baseprescriptionpanel import BasePrescriptionPanel
from .newadmission import BasePage
from .newadmission import PatientSelectorPage
from .newadmission import DoctorBedSelectorPage
from .newadmission import ProblemSelectorPage

ID_REMOVE = wx.NewId()
ID_PRESET_ADD = wx.NewId()
ID_PRESET_REMOVE = wx.NewId()


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



class PrescriptionPage(BasePage, BasePrescriptionPanel):
    """Prescription Page"""
    def __init__(self, parent, session, title):
        BasePage.__init__(self, parent, session, title)
        BasePrescriptionPanel.__init__(self, parent, session)

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




class SubencountersPage(BasePage):
    """Subencounters Page"""
    def __init__(self, parent, session, title):
        super(SubencountersPage, self).__init__(parent, session, title)
        self.subencounter = None

        self.subencounters = []

        self.subencounter_classes = {}
        self.subencounter_fields = {}
        self.subencounter_subtitle_decorators = {}
        self.subencounter_list_decorators = {}
        self.subencounter_titles = {}

        self.toolbar = wx.ToolBar(self, style=wx.TB_VERTICAL | wx.TB_NODIVIDER)
        self.toolbar.AddTool(wx.ID_ADD, "Add", images.get("add_24"), wx.NullBitmap, wx.ITEM_NORMAL, "Add", "")
        self.toolbar.AddTool(ID_REMOVE, "Remove", images.get("delete"), wx.NullBitmap, wx.ITEM_NORMAL, "Remove", "")
        self.toolbar.Realize()

        self.toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_remove, id=ID_REMOVE)

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self.subencounter_list = DbListBox(splitter, self._subencounter_list_decorator)
        self.subencounter_list.Bind(wx.EVT_LISTBOX, self._on_subencounter_selected)

        self.subencounter_form = DbFormSwitcher(splitter, session, style=wx.BORDER_THEME)
        self.subencounter_form.Bind(events.EVT_AM_DB_FORM_CHANGED, self._on_field_changed)

        splitter.SplitVertically(self.subencounter_list, self.subencounter_form, 200)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.toolbar, 0, wx.EXPAND | wx.ALL, border=1)
        hsizer.Add(splitter, 1, wx.EXPAND | wx.ALL, border=1)

        self.sizer.Add(wx.StaticText(self, label=" "), 0, wx.EXPAND | wx.ALL, border=2)
        self.sizer.Add(hsizer, 1, wx.EXPAND | wx.ALL, border=2)

        self.add_menu_id_subencounter_class = {}
        self.add_menu = wx.Menu()


    def add_subencounter_class(self, title, subencounter_class, subencounter_fields, subtitle_decorator=None, list_decorator=None):
        type_name = subencounter_class().__mapper_args__['polymorphic_identity']

        self.subencounter_classes[type_name] = subencounter_class
        self.subencounter_fields[type_name] = subencounter_fields
        self.subencounter_subtitle_decorators[type_name] = subtitle_decorator
        self.subencounter_list_decorators[type_name] = list_decorator
        self.subencounter_titles[type_name] = title

        add_menu_id = wx.NewId()
        self.add_menu_id_subencounter_class[add_menu_id] = subencounter_class
        self.add_menu.Append(add_menu_id, title, "Add {} item".format(title))
        self.add_menu.Bind(wx.EVT_MENU, self._on_add_subencounter, id=add_menu_id)


    def get_subencounters(self):
        return self.subencounters


    def _add_new_subencounter(self, subencounter_class):
        new_subencounter = subencounter_class()
        new_subencounter.start_time = datetime.now()
        new_subencounter.end_time = new_subencounter.start_time
        self.subencounters.append(new_subencounter)
        self._update_subencounter_list()
        self.subencounter_list.SetSelection(len(self.subencounters) - 1)
        self._set_subencounter(new_subencounter)


    def _on_add_subencounter(self, event):
        new_subencounter_class = self.add_menu_id_subencounter_class[event.GetId()]
        self._add_new_subencounter(new_subencounter_class)


    def _on_add(self, event):
        if len(self.subencounter_classes) == 1:
            new_subencounter_class = self.subencounter_classes.values()[0]
            self._add_new_subencounter(new_subencounter_class)
            return
        self.PopupMenu(self.add_menu)


    def _on_remove(self, event):
        selection = self.subencounter_list.get_selected_object()
        try:
            self.subencounters.remove(selection)
        except ValueError:
            pass
        else:
            self._update_subencounter_list()
            self.subencounter_form.unset_object()


    def _on_subencounter_selected(self, event):
        if self.subencounter is not None:
            self.subencounter_form.update_object(self.subencounter)

        selected = self.subencounter_list.get_selected_object()

        self._set_subencounter(selected)


    def _set_subencounter(self, subencounter):
        self.subencounter = subencounter

        if self.subencounter is None:
            self.subencounter_form.unset_object()
            return

        self.subencounter_form.set_object(
            self.subencounter,
            self.subencounter_fields[subencounter.type]
        )


    def _on_field_changed(self, event):
        if self.subencounter is not None:
            self.subencounter_form.update_object(self.subencounter)
        self.subencounter_list.RefreshAll()


    def _update_subencounter_list(self):
        self.subencounter_list.set_items(self.subencounters)


    def _default_list_decorator(self, encounter_object, title, subtitle_decorator=None):
        date_str = config.format_date(encounter_object.start_time)
        html = u'<font size="2"><table width="100%">'\
                    '<tr>'\
                        '<td valign="top">&bull;</td>'\
                        '<td valign="top"><b>{0}</b></td>'\
                        '<td valign="top" width="100%"><b>{1}</b></td>'\
                    '</tr>'\
                    '{2}'\
                '</table></font>'

        subtitle = ""
        if subtitle_decorator is not None:
            subtitle_html = u'<tr>'\
                                '<td></td>'\
                                '<td colspan="2">{}</td>'\
                            '</tr>'
            subtitle = subtitle_html.format(subtitle_decorator(encounter_object))

        return html.format(date_str, title, subtitle)

    def _subencounter_list_decorator(self, encounter_object):
        """Decorator of Subencounter List"""
        type_name = encounter_object.type

        if type_name not in self.subencounter_list_decorators.keys():
            return self._default_list_decorator(encounter_object,
                                                self.subencounter_titles[type_name],
                                                self.subencounter_subtitle_decorators[type_name])

        if self.subencounter_list_decorators[type_name] is None:
            return self._default_list_decorator(encounter_object,
                                                self.subencounter_titles[type_name],
                                                self.subencounter_subtitle_decorators[type_name])

        return self.subencounter_list_decorators[type_name](encounter_object)



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
            DbRelationField("Admitting Doctor", 'personnel', self.session.query(db.Doctor), required=True),
            DbRelationField("Bed", 'discharged_bed', self.session.query(db.Bed), required=True),
            DbDateTimeField("Admission Time", 'start_time', required=True),
            DbDateTimeField("Discharge Time", 'end_time', required=True)
        ]
        self.admission_details_page = FormPage(self, session, "Admission Details", db.Admission, fields)
        self.add_page(self.admission_details_page)

        self.problem_selector = ProblemSelectorPage(self, session)
        self.add_page(self.problem_selector)

        fields = [
            DbMultilineStringField("Cheif Complaints", 'chief_complaints', lines=4),
            DbMultilineStringField("History of Present Illness", 'history', lines=8),
            DbMultilineStringField("Past History", 'past_history', lines=8),
        ]
        self.history_page = FormPage(self, session, "History", db.Admission, fields)
        self.add_page(self.history_page)

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
        self.examination_page = FormPage(self, session, "Examination", db.Admission, fields)
        self.add_page(self.examination_page)

        self.investigations_page = SubencountersPage(self, session, "Investigations && Reports")
        self.add_page(self.investigations_page)

        imaging_fields = [
            DbDateTimeField("Time", 'record_time', required=True),
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
            DbDateTimeField("Time", 'record_time', required=True),
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
            DbDateTimeField("Time", 'record_time', required=True),
            DbStringField("Site", 'site'),
            DbStringField("Pathologist", 'pathologist'),
            DbMultilineStringField("Impression", 'impression'),
            DbMultilineStringField("Report", 'report')
        ]
        self.investigations_page.add_subencounter_class("Histopathology Report",
                                                  db.Histopathology,
                                                  histopathology_fields,
                                                  lambda v: u"{}".format(v.site))

        self.surgical_procedures_page = SubencountersPage(self, session, "Surgical Procedures")
        self.add_page(self.surgical_procedures_page)
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
        self.course_page = FormPage(self, session, "Hospital Course Summary", db.Admission, fields, False)
        self.add_page(self.course_page)

        
        self.complication_page = ComplicationsPage(self, session) #FormPage(self, session, "Surgical Complication Grade", db.ComplicationGrade, fields)
        self.add_page(self.complication_page)

        self.prescription_page = PrescriptionPage(self, session, "Prescription")
        self.add_page(self.prescription_page)

        fields = [
            DbMultilineStringField("Advice", 'discharge_advice', lines=8),
            DbMultilineStringField("Follow Up", 'follow_up', lines=8),
            DbStringField("Discharge Prepared By", 'written_by', required=True)
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

        investigations = self.get_investigations()
        for investigation in investigations:
            admission.add_child_encounter(investigation)

        procedures = self.get_surgical_procedures()
        for procedure in procedures:
            admission.add_child_encounter(procedure)

        #TODO Add Prescription

        return admission


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