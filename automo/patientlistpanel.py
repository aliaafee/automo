"""Patients list panel"""
import wx

import database as db
from dbqueryresultbox import DbQueryResultBox


class PatientListPanel(wx.Panel):
    """Patients list panel"""
    def __init__(self, parent, session, **kwds):
        super(PatientListPanel, self).__init__(parent, **kwds)

        self.session = session

        self.patient_panel = None

        self.all_patients_list = DbQueryResultBox(self, html_decorator=self._patient_list_decorator)
        self.all_patients_list.Bind(wx.EVT_LISTBOX, self._on_patient_selected)
        self.all_patients_list.set_result(
            self.session.query(db.Patient)
        )

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.all_patients_list, 1 , wx.EXPAND | wx.ALL, border=0)
        self.SetSizer(self.sizer)


    def _patient_list_decorator(self, item, query_str):
        return item.name


    def _on_patient_selected(self, event):
        if self.patient_panel.is_unsaved():
            self.patient_panel.save_changes()
            print "Changes saved"

        patient_selected = self.all_patients_list.get_selected_object()

        if patient_selected is None:
            return

        self.patient_panel.set(patient_selected)