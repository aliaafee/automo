"""Discharge list Panel"""
import string
import re
import dateutil.relativedelta as rd
import wx
from sqlalchemy import or_

from .. import config
from .. import database as db

from . import images
from . import events
from .dbqueryresultbox import DbQueryResultBox
from .patientpanel import PatientPanel
from .dischargeeditor import DischargeEditor

ID_OPEN_PATIENT = wx.NewId()
ID_EDIT_DISCHARGE = wx.NewId()

class DischargeListPanel(wx.Panel):
    """Discharge list Panel"""
    def __init__(self, parent, session, **kwds):
        super(DischargeListPanel, self).__init__(parent, **kwds)

        self.session = session

        self.txt_search = wx.TextCtrl(self)
        self.txt_search.Bind(wx.EVT_TEXT, self._on_change_filter)

        self.discharge_list = DbQueryResultBox(self, self._encounter_decorator)
        self.discharge_list.Bind(wx.EVT_LISTBOX, self._on_discharge_selected)
        self.discharge_list.Bind(wx.EVT_RIGHT_DOWN, self._on_context)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.txt_search, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        sizer.Add(self.discharge_list, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(sizer)

        self.context_menu = wx.Menu()
        self.context_menu.Append(ID_EDIT_DISCHARGE, "Edit Discharge", "Open Discharge Editor")
        self.context_menu.Bind(wx.EVT_MENU, self._on_discharge_edit, id=ID_EDIT_DISCHARGE)
        #self.context_menu.Append(ID_OPEN_PATIENT, "Patient File", "Open Patient File in New Window")
        #self.context_menu.Bind(wx.EVT_MENU, self._on_patient_file, id=ID_OPEN_PATIENT)

        self.refresh()


    def _search(self, str_search):
        items = self.session.query(db.Admission)

        items = items.order_by(db.Admission.start_time.desc())

        self.discharge_list.set_result(items, str_search)

        """
        if str_search != "":
            items = items.filter(
                or_(
                    db.Patient.hospital_no.like("%{0}%".format(str_search)),
                    db.Patient.name.like("%{0}%".format(str_search))
                )
            )

            self.discharge_list.set_result(items, str_search)
        else:
            self.discharge_list.clear()
        """


    def _on_context(self, event):
        selected_discharge = self.get_selected()
        if selected_discharge is None:
            return

        self.discharge_list.PopupMenu(self.context_menu)


    def _on_discharge_selected(self, event):
        selected_discharge = self.get_selected()

        event = events.EncounterSelectedEvent(events.ID_ENCOUNTER_SELECTED, object=selected_discharge)
        wx.PostEvent(self, event)


    def get_selected(self):
        selected_discharge = self.discharge_list.get_selected_object()

        return selected_discharge


    def refresh(self):
        """Refresh the panel"""
        self._search(self.txt_search.GetValue())


    def refresh_selected(self):
        self.discharge_list.RefreshSelected()


    def refresh_all(self):
        self.discharge_list.RefreshAll()


    def _on_patient_file(self, event):
        selected_discharge = self.get_selected()
        if selected_discharge is None:
            return

        patient = selected_discharge.patient

        patient_frame = wx.Frame(None, size=(800, 600))
        patient_panel = PatientPanel(patient_frame, self.session)
        patient_panel.toolbar.EnableTool(wx.ID_NEW, False)
        patient_panel.set(patient)
        patient_frame.SetTitle("{0} - {1} - AutoMO".format(patient_panel.patient.hospital_no, patient_panel.patient.name))
        sizer= wx.BoxSizer()
        sizer.Add(patient_panel, wx.EXPAND)
        def _on_patient_changed(event):
            patient_frame.SetTitle("{0} - {1} - AutoMO".format(patient_panel.patient.hospital_no, patient_panel.patient.name))
        patient_frame.Bind(events.EVT_AM_PATIENT_INFO_CHANGED, _on_patient_changed)
        patient_frame.Show()


    def _on_discharge_edit(self, event):
        selected_discharge = self.get_selected()
        if selected_discharge is None:
            return
        patient = selected_discharge.patient

        discharge_frame = wx.Frame(None, size=(800, 600))
        discharge_panel = DischargeEditor(discharge_frame, self.session)

        discharge_frame.SetTitle(
            "Edit Discharge Summary - {hospital_no} - {name} {age}/{sex}".format(
                age=config.format_duration(patient.age),
                **vars(patient)
            )
        )

        discharge_frame.SetIcon(images.get_app_icon())

        discharge_panel.set(selected_discharge)
        discharge_frame.Show()


    def _on_change_filter(self, event):
        self._search(self.txt_search.GetValue())


    def _non_breaking(self, text):
        return string.replace(text, " ", "&nbsp;")


    def _encounter_decorator(self, admission_object, query_string):
        date_str = config.format_date(admission_object.start_time)

        duration_str = ""
        if admission_object.end_time is None:
            duration_str += "(current)"
        else:
            duration_str += "({})".format(
                config.format_duration(
                    rd.relativedelta(
                        admission_object.end_time, admission_object.start_time
                    )
                )
            )

        patient = admission_object.patient
        str_hospital_no = unicode(patient.hospital_no)
        str_name = unicode(patient.name)
        str_age = self._non_breaking(config.format_duration(patient.age))
        str_sex = patient.sex
        patient_str = "{0} {1} {2}/{3}".format(str_hospital_no, str_name, str_age, str_sex)

        diagnoses = []
        for problem in admission_object.problems:
            diagnoses.append(problem.icd10class.preferred)
        diagnoses_str = "</li><li>".join(diagnoses)

        html = u'<font size="2"><table width="100%" cellspacing="0">'\
                    '<tr>'\
                        '<td valign="top">{0}</td>'\
                        '<td width="100%">{2}</td>'\
                        '<td valign="top">{1}</td>'\
                    '</tr>'\
                    '<tr>'\
                        '<td colspan="3"><ul><li>{3}</li></ul></td>'\
                    '</tr>'\
                '</table><hr/></font>'

        return html.format(
            date_str,
            duration_str,
            patient_str,
            diagnoses_str
        )

