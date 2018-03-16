"""Admission Panel"""
import wx

from ... import database as db
from ... import config
from .. import events
from .. import images
from ..widgets import DbRelationCtrl
from .baseclinicalencounterpanel import BaseClinicalEncounterPanel
from ..problempanel import ProblemPanel
from ..measurementspanel import MeasurementsPanel
from ..vitalspanel import VitalsPanel
from ..prescriptionpanel import PrescriptionPanel
from ..bedselector import BedSelectorDialog
from ..encounternotebookform import EncounterNotebookForm
from ..subencounters import Subencounters
from .. import dbform as fm
from ..pdfviewer import PDFViewer

ID_TRANSFER_BED = wx.NewId()
ID_PRINT_DISCHARGE = wx.NewId()
ID_PRINT_PRESCRIPTION = wx.NewId()


class AdmissionPanel(BaseClinicalEncounterPanel):
    """Admission Panel"""
    def __init__(self, parent, session, **kwds):
        super(AdmissionPanel, self).__init__(parent, session, **kwds)

        self.set_title("Admission")

        self.encounter_type = "admission"

        self.txt_bed = DbRelationCtrl(self.info_panel, self.session)

        self.notebook = wx.Notebook(self, style=wx.NB_NOPAGETHEME)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._on_changing_notebook)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_change_notebook)

        self.create_notebook()

        bed_sizer = wx.FlexGridSizer(2, 2, 2, 2)
        bed_sizer.AddMany([
            (wx.StaticText(self.info_panel, label="Bed"), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.txt_bed, 0, wx.EXPAND)
        ])
        bed_sizer.AddSpacer(21)
        self.info_panel_sizer.Add(bed_sizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        self.sizer.Add(self.notebook, 1, wx.EXPAND)

        self.print_menu = wx.Menu()
        self.create_print_menu()
        


    def create_notebook(self):
        admission_note_fields = [
            fm.MultilineStringField("Cheif Complaints", 'chief_complaints', lines=4),
            fm.OptionalMultilineStringField("History of Present Illness", 'history', lines=8),
            fm.OptionalMultilineStringField("Past History", 'past_history', lines=8),
            fm.OptionalMultilineStringField("General Inspection", 'general_inspection', lines=8),
            fm.OptionalMultilineStringField("Head Exam", 'exam_head', lines=8),
            fm.OptionalMultilineStringField("Neck Exam", 'exam_neck', lines=8),
            fm.OptionalMultilineStringField("Chest Exam", 'exam_chest', lines=8),
            fm.OptionalMultilineStringField("Abdomen Exam", 'exam_abdomen', lines=8),
            fm.OptionalMultilineStringField("Genitalia Exam", 'exam_genitalia', lines=8),
            fm.OptionalMultilineStringField("Pelvic/Rectal Exam", 'exam_pelvic_rectal', lines=8),
            fm.OptionalMultilineStringField("Extremities Exam", 'exam_extremities', lines=8),
            fm.OptionalMultilineStringField("Other Exam", 'exam_other', lines=8)
        ]
        self.admission_note_panel = EncounterNotebookForm(self.notebook, self.session, db.Admission,
                                                          admission_note_fields)
        self.notebook.AddPage(self.admission_note_panel, "Admission Notes")

        self.problems_panel = ProblemPanel(self.notebook, self.session)
        self.notebook.AddPage(self.problems_panel, "Diagnosis")

        self.measurements_panel = MeasurementsPanel(self.notebook, self.session)
        self.notebook.AddPage(self.measurements_panel, "Measurements")

        self.vitals_panel = VitalsPanel(self.notebook, self.session)
        self.notebook.AddPage(self.vitals_panel, "Vitals")

        self.subencounters = Subencounters(self.notebook, self.session)
        self.notebook.AddPage(self.subencounters, "Notes && Reports")

        progress_fields = [
            fm.DateTimeField("Time", 'examination_time', required=True),
            fm.RelationField("Doctor", 'personnel', self.session.query(db.Doctor)),
            fm.MultilineStringField("Subjective", 'subjective'),
            fm.MultilineStringField("Objective", 'objective'),
            fm.MultilineStringField("Assessment", 'assessment'),
            fm.MultilineStringField("Plan", 'plan')
        ]
        self.subencounters.add_subencounter_class("Progress Note", db.Progress, progress_fields)

        procedure_fields = [
            fm.StringField("Procedure Name", 'procedure_name'),
            fm.CheckBoxField("Emergency", 'emergency'),
            fm.StringField("Preop Diagnosis", 'preoperative_diagnosis'),
            fm.StringField("Postop Diagnosis", 'postoperative_diagnosis'),
            fm.DateTimeField("Time Started", 'start_time', required=True),
            fm.DateTimeField("Time Completed", 'end_time', required=True),
            fm.RelationField("Surgeon", 'personnel', self.session.query(db.Doctor)),
            fm.StringField("Assistants(s)", 'assistant'),
            fm.StringField("Anesthetist(s)", 'anesthetist'),
            fm.StringField("Nurse(s)", 'nurse'),
            fm.MultilineStringField("Findings", 'findings'),
            fm.MultilineStringField("Steps", 'steps'),
        ]
        self.subencounters.add_subencounter_class("Procedure Note",
                                                  db.SurgicalProcedure,
                                                  procedure_fields,
                                                  lambda v: u"{}".format(v.procedure_name))

        imaging_fields = [
            fm.DateTimeField("Time", 'record_time', required=True),
            fm.StringField("Imaging Type", 'imaging_type'),
            fm.StringField("Site", 'site'),
            fm.StringField("Radiologist", 'radiologist'),
            fm.MultilineStringField("Impression", 'impression'),
            fm.MultilineStringField("Report", 'report')
        ]
        self.subencounters.add_subencounter_class("Imaging Report",
                                                  db.Imaging,
                                                  imaging_fields,
                                                  lambda v: u"{0} {1}".format(v.imaging_type, v.site))

        endoscopy_fields = [
            fm.DateTimeField("Time", 'record_time', required=True),
            fm.StringField("Site", 'site'),
            fm.StringField("Endoscopist", 'endoscopist'),
            fm.MultilineStringField("Impression", 'impression'),
            fm.MultilineStringField("Report", 'report')
        ]
        self.subencounters.add_subencounter_class("Endoscopy Report",
                                                  db.Endoscopy,
                                                  endoscopy_fields,
                                                  lambda v: u"{}".format(v.site))

        histopathology_fields = [
            fm.DateTimeField("Time", 'record_time', required=True),
            fm.StringField("Site", 'site'),
            fm.StringField("Pathologist", 'pathologist'),
            fm.MultilineStringField("Impression", 'impression'),
            fm.MultilineStringField("Report", 'report')
        ]
        self.subencounters.add_subencounter_class("Histopathology Report",
                                                  db.Histopathology,
                                                  histopathology_fields,
                                                  lambda v: u"{}".format(v.site))

        otherreport_fields = [
            fm.DateTimeField("Time", 'record_time', required=True),
            fm.StringField("Name", 'name'),
            fm.StringField("Reported by", 'reported_by'),
            fm.MultilineStringField("Impression", 'impression'),
            fm.MultilineStringField("Report", 'report')
        ]
        self.subencounters.add_subencounter_class("Other Report",
                                                  db.OtherReport,
                                                  otherreport_fields,
                                                  lambda v: u"{}".format(v.name))
        
        other_fields = [
            fm.DateTimeField("Time Started", 'start_time', required=True),
            fm.DateTimeField("Time Completed", 'end_time', required=True),
            fm.StringField("Title", 'title'),
            fm.MultilineStringField("Note", 'note')
        ]
        self.subencounters.add_subencounter_class("Other Note",
                                                  db.OtherEncounter,
                                                  other_fields,
                                                  lambda v: u"{}".format(v.title))

        complication_fields = [
            fm.RelationField("Complication Grade",
                            'complication_grade',
                            self.session.query(db.ComplicationGrade),
                            help_text="\n\n".join(["Grade {0} - {1}".format(v.id, v.description) for v in self.session.query(db.ComplicationGrade).all()])),
            fm.CheckBoxField("Disability on Discharge", 'complication_disability'),
            fm.MultilineStringField("Complication Summary", 'complication_summary', lines=8)
        ]
        self.complication_panel = EncounterNotebookForm(self.notebook, self.session, db.Admission,
                                                          complication_fields)
        self.notebook.AddPage(self.complication_panel, "Complications")

        discharge_note_fields = [
            fm.MultilineStringField("Hospital Course Summary", 'hospital_course', lines=8),
            fm.MultilineStringField("Discharge Advice", 'discharge_advice', lines=8),
            fm.MultilineStringField("Follow Up", 'follow_up', lines=8),
            fm.StringField("Discharge Prepared By", 'written_by')
        ]
        self.discharge_note_panel = EncounterNotebookForm(self.notebook, self.session, db.Admission,
                                                          discharge_note_fields)
        self.notebook.AddPage(self.discharge_note_panel, "Discharge Notes")

        self.prescription_panel = PrescriptionPanel(self.notebook, self.session)
        self.notebook.AddPage(self.prescription_panel, "Prescription")


    def create_toolbar(self):
        self.toolbar.AddTool(wx.ID_PRINT, "Print", images.get("print_24"), wx.NullBitmap, wx.ITEM_NORMAL, "Print", "")
        self.toolbar.AddTool(ID_TRANSFER_BED, "Transfer", images.get("bed_transfer"), wx.NullBitmap, wx.ITEM_NORMAL, "Transfer Bed", "")
        self.toolbar.AddSeparator()

        self.toolbar.Bind(wx.EVT_TOOL, self._on_print, id=wx.ID_PRINT)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_transfer_bed, id=ID_TRANSFER_BED)

        super(AdmissionPanel, self).create_toolbar()


    def create_print_menu(self):
        self.print_menu.Append(ID_PRINT_PRESCRIPTION, "Precription", "Print Prescription")
        self.print_menu.Append(ID_PRINT_DISCHARGE, "Discharge Summary", "Print Discharge Summary")

        self.print_menu.Bind(wx.EVT_MENU, self._on_print_prescription, id=ID_PRINT_PRESCRIPTION)
        self.print_menu.Bind(wx.EVT_MENU, self._on_print_discharge, id=ID_PRINT_DISCHARGE)


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


    def _on_print(self, event):
        self.PopupMenu(self.print_menu)


    def _on_print_prescription(self, event):
        filename = self.encounter.get_prescription_pdf(self.session)

        pdf_view = PDFViewer(None, title="Print Preview - Prescription")
        pdf_view.viewer.UsePrintDirect = False
        pdf_view.viewer.LoadFile(filename)
        pdf_view.Show()


    def _on_print_discharge(self, event):
        filename = self.encounter.generate_discharge_summary(self.session)

        pdf_view = PDFViewer(None, title="Print Preview - Discharge Summary")
        pdf_view.viewer.UsePrintDirect = ``False``
        pdf_view.viewer.LoadFile(filename)
        pdf_view.Show()


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

        if encounter.type != self.encounter_type:
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
