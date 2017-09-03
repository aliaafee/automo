"""Encounters List Panel"""
from dateutil.relativedelta import relativedelta
import wx

from .. import config
from .. import database as db
from . import events
from .dbqueryresultbox import DbQueryResultBox
from .admissionpanel import AdmissionPanel


class EncountersPanel(wx.Panel):
    """Encounters list panel"""
    def __init__(self, parent, session, **kwds):
        super(EncountersPanel, self).__init__(parent, **kwds)

        self.session = session
        self.patient = None

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self.encounters_list = DbQueryResultBox(splitter, self._encounter_decorator)
        self.encounters_list.Bind(wx.EVT_LISTBOX, self._on_encounter_selected)

        self.encounter_panel = AdmissionPanel(splitter, self.session)
        self.encounter_panel.Bind(events.EVT_AM_ENCOUNTER_CHANGED, self._on_encounter_changed)

        splitter.SplitVertically(self.encounters_list, self.encounter_panel)
        splitter.SetMinimumPaneSize(100)
        splitter.SetSashPosition(200)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splitter, 1, wx.EXPAND | wx.ALL, border=0)
        self.SetSizer(sizer)

        self.refresh()


    def _encounter_decorator(self, encounter_object, query_string):
        date_str = ""
        if encounter_object.type == "admission":
            date_str = "Admission"
        elif encounter_object.type == "clinicvisit":
            date_str = "Outpatient"
        date_str += " <b>{0}</b>".format(config.format_date(encounter_object.start_time))
        if encounter_object.end_time is None:
            date_str += " (current)"
        elif encounter_object.type == "admission":
            date_str += " ({})".format(
                config.format_duration(
                    relativedelta(
                        encounter_object.end_time, encounter_object.start_time
                    )
                )
            )

        diagnoses = []
        for problem in encounter_object.problems:
            diagnoses.append(problem.icd10class.preferred)
        diagnoses_str = "</li><li>".join(diagnoses)

        html = u'<font size="2"><table width="100%">'\
                    '<tr>'\
                        '<td>{0}</td>'\
                    '</tr>'\
                    '<tr>'\
                        '<td><ul><li>{1}</li></ul></td>'\
                    '</tr>'\
                '</table></font>'

        return html.format(date_str, diagnoses_str)


    def _on_encounter_selected(self, event):
        selected_encounter = self.encounters_list.get_selected_object()
        if selected_encounter is not None:
            self.encounter_panel.set(selected_encounter)


    def _on_encounter_changed(self, event):
        self.encounters_list.RefreshAll()


    def set_patient(self, patient):
        self.patient = patient

        if patient is None:
            self.unset_patient()
            return

        items = self.session.query(db.Encounter)\
                    .filter(db.Encounter.patient == self.patient)\
                    .filter(db.Encounter.parent == None)\
                    .order_by(db.Encounter.start_time.desc())

        self.encounters_list.set_result(items, "")
        self.encounters_list.SetSelection(0)

        self.encounter_panel.set(self.encounters_list.get_selected_object())


    def unset_patient(self):
        self.patient = None

        self.encounters_list.clear()


    def refresh(self):
        self.set_patient(self.patient)


    def is_unsaved(self):
        if self.encounter_panel.is_unsaved():
            return True
        return False


    def save_changes(self):
        if self.encounter_panel.is_unsaved():
            self.encounter_panel.save_changes()
