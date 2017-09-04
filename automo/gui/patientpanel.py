"""Patient panel"""
import dateutil.relativedelta as rd
import wx

from .. import config

from . import events
from .patientinfo import PatientInfoPanelSmall

from .encounterspanel import EncountersPanel


class PatientPanel(wx.Panel):
    """Patient Panel"""
    def __init__(self, parent, session, **kwds):
        super(PatientPanel, self).__init__(parent, **kwds)

        self.session = session
        self.patient = None

        self.patient_info = PatientInfoPanelSmall(self, session)

        self.notebook = wx.Notebook(self)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._on_changing_notebook)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_change_notebook)

        self.encounters_panel = EncountersPanel(self.notebook, session)
        self.encounters_panel.Bind(events.EVT_AM_ENCOUNTER_CHANGED, self._on_admission_changed)
        self.notebook.AddPage(self.encounters_panel, "Encounters")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.patient_info, 0, wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(sizer)
        self.patient_info.Hide()
        self.notebook.Hide()

        self.Bind(wx.EVT_WINDOW_DESTROY, self._on_close)


    def _on_close(self, event):
        if self.is_unsaved():
            self.save_changes()
            print "Changes saved on window destroy"


    def _admissions_decorator(self, admission_object, query_string):
        date_str = ""
        if admission_object.end_time is None:
            date_str += "<b>{0}</b> (current)".format(
                config.format_date(admission_object.start_time)
            )
        else:
            date_str += "<b>{0}</b> ({1})".format(
                config.format_date(admission_object.start_time),
                config.format_duration(
                    rd.relativedelta(
                        admission_object.end_time, admission_object.start_time
                    )
                )
            )

        diagnoses = []
        for problem in admission_object.problems:
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


    def _on_change_notebook(self, event):
        active_page = self.notebook.GetPage(event.GetSelection())
        active_page.set_patient(self.patient)


    def _on_changing_notebook(self, event):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page.is_unsaved():
            active_page.save_changes()


    def _on_admission_changed(self, event):
        pass


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing"""
        if self.patient is None:
            return False

        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page.is_unsaved():
            return True

        return False


    def save_changes(self):
        if self.patient is None:
            return

        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page.is_unsaved():
            active_page.save_changes()


    def refresh(self):
        """Refresh Contents of Panel"""
        if self.patient is None:
            return
        
        if self.is_unsaved():
            self.save_changes()
            print "Changes saved"

        self.set(self.patient)


    def unset(self):
        """Unset selected patient"""
        self.patient = None

        self.patient_info.unset()

        self.patient_info.Hide()
        self.notebook.Hide()


    def set(self, patient):
        """Set selected patient"""
        if patient is None:
            self.unset()
            return

        self.patient = patient

        self.patient_info.set(self.patient)

        self.patient_info.Show()
        self.notebook.Show()

        self.Layout()

        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        active_page.set_patient(self.patient)