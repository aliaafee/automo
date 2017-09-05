"""Admission Panel"""
import wx

from .. import database as db
from . import events
from .dbrelationctrl import DbRelationCtrl
from .dbrelationcombo import DbRelationCombo
from .dbdatepicker import DbDatePicker
from .problempanel import ProblemPanel
from .encounternote import EncounterNote
from .measurementspanel import MeasurementsPanel


class AdmissionPanel(wx.Panel):
    """Admission Panel"""
    def __init__(self, parent, session, **kwds):
        super(AdmissionPanel, self).__init__(parent, **kwds)

        self.session = session
        self.admission = None

        self.editable = True

        label_width = 60

        self.lbl_bed = wx.StaticText(self, label="Bed",
                                     size=wx.Size(label_width, -1))
        self.txt_bed = DbRelationCtrl(self, self.session)

        self.lbl_admitting_doctor = wx.StaticText(self, label="Doctor",
                                                  size=wx.Size(label_width, -1))
        self.txt_admitting_doctor = DbRelationCombo(self, self.session)

        self.lbl_admitted_date = wx.StaticText(self, label="Admitted",
                                               size=wx.Size(label_width, -1))
        self.txt_admitted_date = DbDatePicker(self, self.session)
        self.txt_admitted_date.Bind(events.EVT_AM_DB_CTRL_CHANGED, self._on_change_admission)

        self.lbl_discharged_date = wx.StaticText(self, label="Discharged",
                                                 size=wx.Size(label_width, -1))
        self.txt_discharged_date = DbDatePicker(self, self.session)
        self.txt_discharged_date.Bind(events.EVT_AM_DB_CTRL_CHANGED, self._on_change_admission)

        self.notebook = wx.Notebook(self)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._on_changing_notebook)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_change_notebook)

        self.problems_panel = ProblemPanel(self.notebook, self.session)
        self.problems_panel.Bind(events.EVT_AM_PROBLEM_CHANGED, self._on_change_admission)
        self.notebook.AddPage(self.problems_panel, "Diagnosis")

        self.admission_note_panel = EncounterNote(self.notebook, self.session, 'admission_note')
        self.notebook.AddPage(self.admission_note_panel, "Admission Note")

        self.progress_notes_panel = EncounterNote(self.notebook, self.session, 'progress_note')
        self.notebook.AddPage(self.progress_notes_panel, "Progress Notes")

        self.measurements_panel = MeasurementsPanel(self.notebook, self.session)
        self.notebook.AddPage(self.measurements_panel, "Measurements")

        self.discharge_note_panel = EncounterNote(self.notebook, self.session, 'discharge_note')
        self.notebook.AddPage(self.discharge_note_panel, "Discharge Note")

        grid_sizer = wx.FlexGridSizer(2, 4, 2, 2)
        grid_sizer.AddGrowableCol(1, 1)
        grid_sizer.AddGrowableCol(3, 1)
        lbl_flags = wx.SizerFlags(1).Align(wx.ALIGN_CENTER_VERTICAL)
        txt_flags = wx.SizerFlags(1).Expand()
        grid_sizer.AddF(self.lbl_bed, lbl_flags)
        grid_sizer.AddF(self.txt_bed, txt_flags)
        grid_sizer.AddF(self.lbl_admitting_doctor, lbl_flags)
        grid_sizer.AddF(self.txt_admitting_doctor, txt_flags)
        grid_sizer.AddF(self.lbl_admitted_date, lbl_flags)
        grid_sizer.AddF(self.txt_admitted_date, txt_flags)
        grid_sizer.AddF(self.lbl_discharged_date, lbl_flags)
        grid_sizer.AddF(self.txt_discharged_date, txt_flags)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid_sizer, 0, wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(sizer)

        self.Layout()

        self.unset()


    def _on_toggle_editable(self, event):
        self.set_editable(not self.editable)


    def _on_change_admission(self, event):
        event = events.EncounterChangedEvent(object=event.object)
        wx.PostEvent(self, event)


    def _on_change_notebook(self, event):
        active_page = self.notebook.GetPage(event.GetSelection())
        active_page.set_encounter(self.admission)
        active_page.set_editable(self.editable)


    def _on_changing_notebook(self, event):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page.is_unsaved():
            active_page.save_changes()
            print "Changes saved"
            #event.Veto() to cancel switch to new tab


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing"""
        if self.admission is None:
            return False

        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page.is_unsaved():
            return True
        return False


    def save_changes(self):
        """Save changes"""
        if self.admission is None:
            return

        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        active_page.save_changes()


    def set_editable(self, editable):
        """Set control to editable or not"""
        self.editable = editable

        active_page = self.notebook.GetPage(self.notebook.GetSelection())

        if self.editable:
            self.txt_admitted_date.Enable()
            self.txt_discharged_date.Enable()
            self.txt_admitting_doctor.Enable()
            active_page.set_editable(True)
        else:
            self.txt_admitted_date.Disable()
            self.txt_discharged_date.Disable()
            self.txt_admitting_doctor.Disable()
            active_page.set_editable(False)


    def set(self, admission):
        """Set the admission"""
        self.admission = admission

        if self.admission is None:
            self.unset()
            return

        if self.admission.type != 'admission':
            self.unset()
            return

        self.lbl_admitted_date.Show()
        self.lbl_admitting_doctor.Show()
        self.lbl_bed.Show()
        self.lbl_discharged_date.Show()

        self.txt_admitted_date.Show()
        self.txt_admitting_doctor.Show()
        self.txt_bed.Show()
        self.txt_discharged_date.Show()

        self.txt_admitted_date.set_dbobject_attr(admission, "start_time")
        self.txt_discharged_date.set_dbobject_attr(admission, "end_time")

        doctors = self.session.query(db.Doctor)
        self.txt_admitting_doctor.set_dbobject_attr(admission, "personnel_id",
                                                    "personnel", doctors, "id")

        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        active_page.set_encounter(self.admission)
        self.notebook.Show()

        if self.admission.is_active():
            """This is the current admission"""
            self.set_editable(True)
            self.lbl_discharged_date.Hide()
            self.txt_discharged_date.Hide()
            self.txt_bed.set_dbobject_attr(admission, "bed_id", "bed")
        else:
            """This is one of the previous admissions
              These are not editable by default"""
            self.set_editable(False)
            self.txt_bed.set_dbobject_attr(admission, "discharged_bed_id", "discharged_bed")

        self.Layout()


    def unset(self):
        """Clear the panel"""
        self.admission = None

        self.lbl_admitted_date.Hide()
        self.lbl_admitting_doctor.Hide()
        self.lbl_bed.Hide()
        self.lbl_discharged_date.Hide()

        self.txt_admitted_date.Hide()
        self.txt_admitting_doctor.Hide()
        self.txt_bed.Hide()
        self.txt_discharged_date.Hide()

        self.txt_bed.set_dbobject_attr(None, "", "")
        self.txt_admitted_date.set_dbobject_attr(None, "")
        self.txt_discharged_date.set_dbobject_attr(None, "")
        self.txt_admitting_doctor.set_dbobject_attr(None, "", "", None, "")

        self.notebook.Hide()
