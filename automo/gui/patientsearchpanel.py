"""Patient Search Panel"""
import string
import re
import wx
from sqlalchemy import or_

from .. import config
from .. import database as db

from . import events
from .widgets import DbQueryResultBox


class PatientSearchPanel(wx.Panel):
    """Patient Search Panel"""
    def __init__(self, parent, session, **kwds):
        super(PatientSearchPanel, self).__init__(parent, **kwds)

        self.session = session

        self.txt_search = wx.TextCtrl(self)
        self.txt_search.Bind(wx.EVT_TEXT, self._on_change_filter)

        self.patients_list = DbQueryResultBox(self, self._patient_decorator)
        self.patients_list.Bind(wx.EVT_LISTBOX, self._on_patient_selected)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.txt_search, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        sizer.Add(self.patients_list, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(sizer)

        self.refresh()


    def _search(self, str_search):
        items = self.session.query(db.Patient)

        if str_search != "":
            items = items.filter(
                or_(
                    or_(
                        db.Patient.hospital_no.like("%{0}%".format(str_search)),
                        db.Patient.national_id_no.like("%{0}%".format(str_search))
                    ),
                    db.Patient.name.like("%{}%".format(str_search))
                )
            )

            self.patients_list.set_result(items, str_search)
        else:
            self.patients_list.clear()


    def _on_patient_selected(self, event):
        selected_patient = self.get_selected()

        event = events.PatientSelectedEvent(events.ID_PATIENT_SELECTED, object=selected_patient)
        wx.PostEvent(self, event)


    def get_selected(self):
        selected_patient = self.patients_list.get_selected_object()

        return selected_patient


    def refresh(self):
        """Refresh the panel"""
        self._search(self.txt_search.GetValue())


    def refresh_selected(self):
        self.patients_list.RefreshSelected()


    def refresh_all(self):
        self.patients_list.RefreshAll()


    def _on_change_filter(self, event):
        self._search(self.txt_search.GetValue())


    def _non_breaking(self, text):
        return string.replace(text, " ", "&nbsp;")


    def _higlight_query(self, value, query_string):
        str_value = unicode(value)
        result = re.search(re.escape(query_string), str_value, re.IGNORECASE)
        if result is not None:
            group = unicode(result.group())
            str_value = string.replace(str_value, group, u'<b>' + group + u'</b>', 1)
        return str_value


    def _patient_decorator(self, patient, query_string):
        str_hospital_no = unicode(patient.hospital_no)
        str_national_id_no = unicode(patient.national_id_no)
        str_name = unicode(patient.name)

        if len(query_string) != 0:
            str_hospital_no = self._higlight_query(str_hospital_no, query_string)
            str_national_id_no = self._higlight_query(str_national_id_no, query_string)
            str_name = self._higlight_query(str_name, query_string)
    
        html = '<font size="2">'\
                    '<table width="100%">'\
                        '<tr>'\
                            '<td valign="top" width="40">{0}</td>'\
                            '<td valign="top" width="40">{1}</td>'\
                            '<td valign="top" width="100%">{2}</td>'\
                            '<td valign="top">{3}/{4}</td>'\
                        '</tr>'\
                    '</table>'\
                '</font>'
        return html.format(
            str_hospital_no,
            str_national_id_no,
            str_name,
            self._non_breaking(config.format_duration(patient.age)),
            patient.sex
        )



class PatientSearchPanelAdv(wx.Panel):
    """Advanced Patient Search Panel"""
    def __init__(self, parent, session, **kwds):
        super(PatientSearchPanelAdv, self).__init__(parent, **kwds)

