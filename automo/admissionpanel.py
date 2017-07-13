"""
Admission Panel
"""
import wx

from dbdatepicker import DbDatePicker
from dbrelationctrl import DbRelationCtrl
from conditionpanel import ConditionPanel
from prescriptionpanel import PrescriptionPanel
from admissionnotes import AdmissionNotesPanel,\
                           ProgressNotesPanel,\
                           DischargeSummaryPanel


class AdmissionPanel(wx.Panel):
    """
    Admission Panel
    """
    def __init__(self, parent, session, **kwds):
        super(AdmissionPanel, self).__init__(parent, **kwds)

        self.session = session
        self.admission = None

        self.editable = True

        sizer = wx.BoxSizer(wx.VERTICAL)

        grid_sizer = wx.FlexGridSizer(5, 2, 2, 2)
        grid_sizer.AddGrowableCol(1, 1)

        lbl_flags = wx.SizerFlags(1).Align(wx.ALIGN_CENTER_VERTICAL)
        txt_flags = wx.SizerFlags(1).Expand()

        label_width = 100

        self.lbl_bed = wx.StaticText(self, label="Bed",
                                     size=wx.Size(label_width, -1))
        self.txt_bed = DbRelationCtrl(self, self.session)
        grid_sizer.AddF(self.lbl_bed, lbl_flags)
        grid_sizer.AddF(self.txt_bed, txt_flags)

        self.lbl_discharged_bed = wx.StaticText(self, label="Bed*",
                                                size=wx.Size(label_width, -1))
        self.txt_discharged_bed = DbRelationCtrl(self, self.session)
        grid_sizer.AddF(self.lbl_discharged_bed, lbl_flags)
        grid_sizer.AddF(self.txt_discharged_bed, txt_flags)

        self.lbl_admitting_doctor = wx.StaticText(self, label="Doctor",
                                                  size=wx.Size(label_width, -1))
        self.txt_admitting_doctor = DbRelationCtrl(self, self.session)
        grid_sizer.AddF(self.lbl_admitting_doctor, lbl_flags)
        grid_sizer.AddF(self.txt_admitting_doctor, txt_flags)

        self.lbl_admitted_date = wx.StaticText(self, label="Admitted",
                                               size=wx.Size(label_width, -1))
        self.txt_admitted_date = DbDatePicker(self, self.session)
        self.txt_admitted_date.Disable()
        grid_sizer.AddF(self.lbl_admitted_date, lbl_flags)
        grid_sizer.AddF(self.txt_admitted_date, txt_flags)

        self.lbl_discharged_date = wx.StaticText(self, label="Discharged",
                                                 size=wx.Size(label_width, -1))
        self.txt_discharged_date = DbDatePicker(self, self.session)
        self.txt_discharged_date.Disable()
        grid_sizer.AddF(self.lbl_discharged_date, lbl_flags)
        grid_sizer.AddF(self.txt_discharged_date, txt_flags)

        sizer.Add(grid_sizer, 0, wx.EXPAND | wx.ALL, border=5)

        self.notebook = wx.Notebook(self)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._on_changing_notebook)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_change_notebook)
        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, border=5)

        self.conditions_panel = ConditionPanel(self.notebook, self.session)
        self.notebook.AddPage(self.conditions_panel, "Conditions")

        self.admission_notes_panel = AdmissionNotesPanel(self.notebook, self.session)
        self.notebook.AddPage(self.admission_notes_panel, "Admission Notes")

        self.progress_notes_panel = ProgressNotesPanel(self.notebook, self.session)
        self.notebook.AddPage(self.progress_notes_panel, "Progress Notes")

        self.prescription_panel = PrescriptionPanel(self.notebook, self.session)
        self.notebook.AddPage(self.prescription_panel, "Prescription")

        self.discharge_summary_panel = DischargeSummaryPanel(self.notebook, self.session)
        self.notebook.AddPage(self.discharge_summary_panel, "Discharge Summary")

        self.SetSizer(sizer)

        self.unset()


    def _on_change_notebook(self, event):
        active_page = self.notebook.GetPage(event.GetSelection())
        active_page.set_admission(self.admission, self.editable)
        event.Skip()


    def _on_changing_notebook(self, event):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page.is_unsaved():
            active_page.save_changes()
            print "Changes saved"


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

        if self.editable:
            #TODO: set things that should happen if editable
            pass
        else:
            #TODO: set things that should happen if not editable
            pass


    def set(self, admission):
        """Set the admission"""
        self.admission = admission

        self.lbl_admitted_date.Show()
        self.lbl_admitting_doctor.Show()
        self.lbl_bed.Show()
        self.lbl_discharged_bed.Show()
        self.lbl_discharged_date.Show()

        self.txt_admitted_date.Show()
        self.txt_admitting_doctor.Show()
        self.txt_bed.Show()
        self.txt_discharged_bed.Show()
        self.txt_discharged_date.Show()

        self.txt_bed.set_dbobject_attr(admission, "bed_id", "bed")
        self.txt_discharged_bed.set_dbobject_attr(admission, "discharged_bed_id",
                                                  "discharged_bed")
        self.txt_admitted_date.set_dbobject_attr(admission, "admitted_date")
        self.txt_discharged_date.set_dbobject_attr(admission, "discharged_date")
        self.txt_admitting_doctor.set_dbobject_attr(admission, "admitting_doctor_id",
                                                    "admitting_doctor")

        if self.admission.discharged_date is None:
            """This is the current admission"""
            self.set_editable(True)
            self.lbl_discharged_date.Hide()
            self.lbl_discharged_bed.Hide()
            self.txt_discharged_date.Hide()
            self.txt_discharged_bed.Hide()
        else:
            """This is one of the previous admissions
              These are not editable by default"""
            self.set_editable(False)
            self.lbl_bed.Hide()
            self.txt_bed.Hide()

        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        active_page.set_admission(self.admission, self.editable)
        self.notebook.Show()

        self.Layout()


    def unset(self):
        """Clear the panel"""
        self.admission = None

        self.lbl_admitted_date.Hide()
        self.lbl_admitting_doctor.Hide()
        self.lbl_bed.Hide()
        self.lbl_discharged_bed.Hide()
        self.lbl_discharged_date.Hide()

        self.txt_admitted_date.Hide()
        self.txt_admitting_doctor.Hide()
        self.txt_bed.Hide()
        self.txt_discharged_bed.Hide()
        self.txt_discharged_date.Hide()

        self.txt_bed.set_dbobject_attr(None, "", "")
        self.txt_discharged_bed.set_dbobject_attr(None, "", "")
        self.txt_admitted_date.set_dbobject_attr(None, "")
        self.txt_discharged_date.set_dbobject_attr(None, "")
        self.txt_admitting_doctor.set_dbobject_attr(None, "", "")

        self.notebook.Hide()
