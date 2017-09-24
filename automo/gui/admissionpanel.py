"""Admission Panel"""
import wx

from .. import database as db
from .. import config
from . import events
from . import images
from .dbrelationctrl import DbRelationCtrl
from .baseclinicalencounterpanel import BaseClinicalEncounterPanel
from .problempanel import ProblemPanel
from .encounternote import EncounterNote
from .measurementspanel import MeasurementsPanel
from .vitalspanel import VitalsPanel
from .prescriptionpanel import PrescriptionPanel
from .bedselector import BedSelectorDialog
from .surgerypanel import SurgeryPanel
from .progresspanel import ProgressPanel
from .encounternotebookform import EncounterNotebookForm
from .encounternotebookpage import EncounterNotebookPage
from .dbform import DbMultilineStringField

ID_TRANSFER_BED = wx.NewId()

class AdmissionPanel(BaseClinicalEncounterPanel):
    """Admission Panel"""
    def __init__(self, parent, session, **kwds):
        super(AdmissionPanel, self).__init__(parent, session, **kwds)

        self.set_title("Admission")

        self.txt_bed = DbRelationCtrl(self.info_panel, self.session)

        self.notebook = wx.Notebook(self)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._on_changing_notebook)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_change_notebook)

        self.problems_panel = ProblemPanel(self.notebook, self.session)
        self.notebook.AddPage(self.problems_panel, "Diagnosis")

        admission_note_fields = [
            DbMultilineStringField("History", 'history', lines=8),
            DbMultilineStringField("Examination", 'examination', lines=8)
        ]
        self.admission_note_panel = EncounterNotebookForm(self.notebook, self.session, db.Admission,
                                                          admission_note_fields)
        self.notebook.AddPage(self.admission_note_panel, "Admission Notes")

        self.progress_notes_panel = ProgressPanel(self.notebook, self.session)
        self.notebook.AddPage(self.progress_notes_panel, "Progress Notes")

        self.surgery_panel = SurgeryPanel(self.notebook, self.session)
        self.notebook.AddPage(self.surgery_panel, "Surgeries")

        self.measurements_panel = MeasurementsPanel(self.notebook, self.session)
        self.notebook.AddPage(self.measurements_panel, "Measurements")

        self.vitals_panel = VitalsPanel(self.notebook, self.session)
        self.notebook.AddPage(self.vitals_panel, "Vitals")

        self.investigation_panel = EncounterNotebookPage(self.notebook, self.session)
        self.notebook.AddPage(self.investigation_panel, "Investigations")

        discharge_note_fields = [
            DbMultilineStringField("Discharge Advice", 'discharge_advice', lines=8),
            DbMultilineStringField("Follow Up", 'follow_up', lines=8)
        ]
        self.discharge_note_panel = EncounterNotebookForm(self.notebook, self.session, db.Admission,
                                                          discharge_note_fields)
        self.notebook.AddPage(self.discharge_note_panel, "Discharge Notes")

        self.prescription_panel = PrescriptionPanel(self.notebook, self.session)
        self.notebook.AddPage(self.prescription_panel, "Prescription")

        bed_sizer = wx.FlexGridSizer(2, 2, 2, 2)
        bed_sizer.AddMany([
            (wx.StaticText(self.info_panel, label="Bed"), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.txt_bed, 0, wx.EXPAND)
        ])
        bed_sizer.AddSpacer(21)
        self.info_panel_sizer.Add(bed_sizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        self.sizer.Add(self.notebook, 1, wx.EXPAND)


    def create_toolbar(self):
        self.toolbar.AddLabelTool(ID_TRANSFER_BED, "Transfer", images.get("bed_transfer"), wx.NullBitmap, wx.ITEM_NORMAL, "Transfer Bed", "")
        self.toolbar.Bind(wx.EVT_TOOL, self._on_transfer_bed, id=ID_TRANSFER_BED)

        self.toolbar.AddSeparator()

        super(AdmissionPanel, self).create_toolbar()


    def _on_transfer_bed(self, event):
        if self.encounter.is_active():
            is_active = True
            current_bed = self.encounter.bed
        else:
            is_active = False
            current_bed = self.encounter.discharged_bed

        with BedSelectorDialog(self, self.session, current_bed=current_bed, empty_beds=False) as selector:
            selector.CenterOnParent()
            if selector.ShowModal() == wx.ID_OK:
                new_bed = selector.get_bed()
                if not is_active:
                    self.encounter.discharged_bed = new_bed
                    self.session.commit()
                    self.refresh()
                    new_event = events.EncounterChangedEvent(events.ID_ENCOUNTER_CHANGED, object=new_bed) 
                    wx.PostEvent(self, new_event)
                else:
                    if new_bed.admission is None:
                        self.encounter.bed = new_bed
                        self.session.commit()
                        self.refresh()
                        new_event = events.PatientInfoChangedEvent(events.ID_PATIENT_INFO_CHANGED, object=self.encounter.bed) 
                        wx.PostEvent(self, new_event)
                        new_event = events.EncounterChangedEvent(events.ID_ENCOUNTER_CHANGED, object=new_bed) 
                        wx.PostEvent(self, new_event)
                    else:
                        message = "Bed {0} is occupied by the following patient, "\
                                  "do you want to exchange the two beds?\n\n{1}\t{2}\t{3}\\{4}"
                        message = message.format(
                            new_bed,
                            new_bed.admission.patient.hospital_no,
                            new_bed.admission.patient.name,
                            config.format_duration(new_bed.admission.patient.age),
                            new_bed.admission.patient.sex
                        )
                        with wx.MessageDialog(None, message, "Exchange Beds",
                                              wx.YES_NO | wx.ICON_QUESTION) as dlg:
                            if dlg.ShowModal() == wx.ID_YES:
                                current_bed = self.encounter.bed
                                new_bed.admission.bed = current_bed
                                self.encounter.bed = new_bed
                                self.session.commit()
                                self.refresh()
                                new_event = events.PatientInfoChangedEvent(events.ID_PATIENT_INFO_CHANGED, object=self.encounter.bed) 
                                wx.PostEvent(self, new_event)
                                new_event = events.EncounterChangedEvent(events.ID_ENCOUNTER_CHANGED, object=new_bed) 
                                wx.PostEvent(self, new_event)


    def _on_change_notebook(self, event):
        active_page = self.notebook.GetPage(event.GetSelection())
        active_page.set_encounter(self.encounter)
        active_page.set_editable(self.editable)


    def _on_changing_notebook(self, event):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page.is_unsaved():
            active_page.save_changes()
            print "Changes saved"
            #event.Veto() to cancel switch to new tab


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing"""
        if self.encounter is None:
            return False

        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page.is_unsaved():
            return True
        return False


    def save_changes(self):
        """Save changes"""
        if self.encounter is None:
            return

        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        active_page.save_changes()


    def set_editable_TODELE(self, editable):
        """Set control to editable or not"""
        super(AdmissionPanel, self).set_editable(editable)

        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if self.editable:
            active_page.set_editable(True)
            self.toolbar.EnableTool(ID_TRANSFER_BED, True)
        else:
            active_page.set_editable(False)
            self.toolbar.EnableTool(ID_TRANSFER_BED, False)


    def editable_on(self):
        super(AdmissionPanel, self).editable_on()
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        active_page.set_editable(True)
        self.toolbar.EnableTool(ID_TRANSFER_BED, True)


    def editable_off(self):
        super(AdmissionPanel, self).editable_off()
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        active_page.set_editable(False)
        self.toolbar.EnableTool(ID_TRANSFER_BED, False)


    def set(self, encounter, refresh=False):
        """Set The Encounter"""
        if encounter is None:
            self.unset()
            return

        if encounter.type != "admission":
            self.unset()
            return

        super(AdmissionPanel, self).set(encounter, refresh=refresh)

        if self.encounter.is_active():
            self.txt_bed.set_dbobject_attr(encounter, "bed_id", "bed")
        else:
            self.txt_bed.set_dbobject_attr(encounter, "discharged_bed_id", "discharged_bed")

        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        active_page.set_encounter(self.encounter)
        self.notebook.Show()


    def unset(self):
        """Clear the panel"""
        super(AdmissionPanel, self).unset()

        self.txt_bed.set_dbobject_attr(None, "", "")

        self.notebook.Hide()
