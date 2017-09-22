"""Patient panel"""
import dateutil.relativedelta as rd
import wx

from .. import database as db
from .. import config

from . import events
from . import images
from .patientinfo import PatientInfoPanelSmall, PatientForm
from .encounterspanel import EncountersPanel
from .newadmission import NewAdmissionDialog

ID_ADMIT = wx.NewId()
ID_DISCHARGE = wx.NewId()


class PatientPanel(wx.Panel):
    """Patient Panel"""
    def __init__(self, parent, session, **kwds):
        super(PatientPanel, self).__init__(parent, **kwds)

        self.session = session
        self.patient = None

        self.patient_info = PatientInfoPanelSmall(self, session)

        self.toolbar = self.patient_info.toolbar
        self.toolbar.AddStretchableSpace()
        self.toolbar.AddLabelTool(wx.ID_EDIT, "Edit", images.get("edit_24"), wx.NullBitmap, wx.ITEM_NORMAL, "Edit Patient", "")
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(ID_ADMIT, "Admit", images.get("admit"), wx.NullBitmap, wx.ITEM_NORMAL, "Admit Patient", "")
        self.toolbar.AddLabelTool(ID_DISCHARGE, "Discharge", images.get("discharge"), wx.NullBitmap, wx.ITEM_NORMAL, "Discharge Patient", "")
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(wx.ID_NEW, "Open", images.get("new_widow_24"), wx.NullBitmap, wx.ITEM_NORMAL, "Open in New Window", "")
        self.toolbar.Realize()

        self.toolbar.Bind(wx.EVT_TOOL, self._on_edit, id=wx.ID_EDIT)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_new_window, id=wx.ID_NEW)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_discharge, id=ID_DISCHARGE)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_admit, id=ID_ADMIT)
        
        #self.notebook = wx.Notebook(self)
        #self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._on_changing_notebook)
        #self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_change_notebook)

        #self.encounters_panel = EncountersPanel(self.notebook, session)
        self.encounters_panel = EncountersPanel(self, session)
        self.Bind(events.EVT_AM_PATIENT_INFO_CHANGED, self._on_patient_info_changed)
        #self.notebook.AddPage(self.encounters_panel, "Encounters")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.patient_info, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        #sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.encounters_panel, 1, wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(sizer)
        self.patient_info.Hide()
        #self.notebook.Hide()
        self.encounters_panel.Hide()

        self.Bind(wx.EVT_WINDOW_DESTROY, self._on_close)


    def _on_edit(self, event):
        with PatientForm(self, title="Edit Patient") as editor:
            editor.CenterOnParent()
            editor.set_object(self.patient)
            if editor.ShowModal() == wx.ID_OK:
                editor.update_object(self.patient)
                self.session.commit()
                event = events.PatientInfoChangedEvent(events.ID_PATIENT_INFO_CHANGED, object=self.patient)
                wx.PostEvent(self, event)


    def _on_discharge(self, event):
        try:
            self.patient.discharge(self.session)
        except Exception as e:
            self.session.rollback()
            with wx.MessageDialog(None,
                "Error Occured. {}".format(e.message),
                "Error",
                wx.OK | wx.ICON_EXCLAMATION) as err_dlg:
                err_dlg.ShowModal()
        else:
            self.session.commit()
            event = events.PatientInfoChangedEvent(events.ID_PATIENT_INFO_CHANGED, object=self.patient)
            wx.PostEvent(self, event)
            new_event = events.EncounterChangedEvent(events.ID_ENCOUNTER_CHANGED, object=self.patient) 
            wx.PostEvent(self.encounters_panel, new_event)


    def _on_admit(self, event):
        with NewAdmissionDialog(self, self.session, patient=self.patient) as dlg:
            done = False
            while not done:
                dlg.ShowModal()
                if dlg.GetReturnCode() == wx.ID_OK:
                    try:
                        patient = self.patient
                        doctor = dlg.get_doctor()
                        bed = dlg.get_bed()
                        problems = dlg.get_problems()
                        admission = patient.admit(self.session, doctor, bed)
                        for problem in problems:
                            patient.problems.append(problem)
                            admission.add_problem(problem)
                    except db.dbexception.AutoMODatabaseError as e:
                        self.session.rollback()
                        with wx.MessageDialog(None,
                            "Database Error Occured. {}".format(e.message),
                            "Database Error",
                            wx.OK | wx.ICON_EXCLAMATION) as err_dlg:
                            err_dlg.ShowModal()
                    except Exception as e:
                        self.session.rollback()
                        with wx.MessageDialog(None,
                            "Error Occured. {}".format(e.message),
                            "Error",
                            wx.OK | wx.ICON_EXCLAMATION) as err_dlg:
                            err_dlg.ShowModal()
                    else:
                        self.session.commit()
                        self.refresh()
                        event = events.PatientInfoChangedEvent(events.ID_PATIENT_INFO_CHANGED, object=self.patient)
                        wx.PostEvent(self, event)
                        done = True
                else:
                    done = True


    def _on_new_window(self, event):
        patient_frame = wx.Frame(None)
        patient_panel = PatientPanel(patient_frame, self.session)
        patient_panel.toolbar.EnableTool(wx.ID_NEW, False)
        patient_panel.set(self.patient)
        patient_frame.SetTitle("{0} - {1} - AutoMO".format(patient_panel.patient.hospital_no, patient_panel.patient.name))
        sizer= wx.BoxSizer()
        sizer.Add(patient_panel, wx.EXPAND)
        def _on_patient_changed(event):
            patient_frame.SetTitle("{0} - {1} - AutoMO".format(patient_panel.patient.hospital_no, patient_panel.patient.name))
        patient_frame.Bind(events.EVT_AM_PATIENT_INFO_CHANGED, _on_patient_changed)
        patient_frame.Show()
        self.unset()


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


    #def _on_change_notebook(self, event):
    #    active_page = self.notebook.GetPage(event.GetSelection())
    #    active_page.set_patient(self.patient)


    #def _on_changing_notebook(self, event):
    #    active_page = self.notebook.GetPage(self.notebook.GetSelection())
    #    if active_page.is_unsaved():
    #        active_page.save_changes()


    def _on_patient_info_changed(self, event):
        self.patient_info.refresh()
        event.Skip()
        self._update_toolbar()


    def _update_toolbar(self):
        current_encounter = self.patient.get_current_encounter(self.session)
        if current_encounter is None:
            self.toolbar.EnableTool(ID_DISCHARGE, False)
            self.toolbar.EnableTool(ID_ADMIT, True)
        else:
            self.toolbar.EnableTool(ID_DISCHARGE, True)
            self.toolbar.EnableTool(ID_ADMIT, False)


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing"""
        if self.patient is None:
            return False

        #active_page = self.notebook.GetPage(self.notebook.GetSelection())
        #if active_page.is_unsaved():
        #    return True
        if self.encounters_panel.is_unsaved():
            return True

        return False


    def save_changes(self):
        if self.patient is None:
            return

        #active_page = self.notebook.GetPage(self.notebook.GetSelection())
        #if active_page.is_unsaved():
        #    active_page.save_changes()
        if self.encounters_panel.is_unsaved():
            self.encounters_panel.save_changes()


    def refresh(self):
        """Refresh Contents of Panel"""
        if self.patient is None:
            return
        
        if self.is_unsaved():
            self.save_changes()
            print "Changes saved"

        self.set(self.patient, refresh=True)


    def unset(self):
        """Unset selected patient"""
        self.patient = None

        self.patient_info.unset()

        self.patient_info.Hide()
        #self.notebook.Hide()
        self.encounters_panel.Hide()


    def set(self, patient, refresh=False):
        """Set selected patient"""
        if patient is None:
            self.unset()
            return

        self.patient = patient

        self.patient_info.set(self.patient)

        self.patient_info.Show()
        #self.notebook.Show()
        self.encounters_panel.Show()

        current_encounter = self.patient.get_current_encounter(self.session)
        self._update_toolbar()

        self.Layout()

        #active_page = self.notebook.GetPage(self.notebook.GetSelection())
        #active_page.set_patient(self.patient)
        if refresh:
            self.encounters_panel.refresh()
        else:
            self.encounters_panel.set_patient(self.patient)
