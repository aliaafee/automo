"""C Ward Interface"""
import tempfile
import wx
import PyPDF2

from .. import database as db
from . import events
from . import images
from .wardinterface import WardInterface
from .batchpatientimporter import BatchPatientImporter
from .newadmission import NewAdmissionDialog
from .pdfviewer import PDFViewer

ID_IMPORT_PATIENTS = wx.NewId()
ID_PRINT_ADMISSION_MULTIPLE = wx.NewId()
ID_PRINT_OT_NOTE = wx.NewId()


def circum_admit_patient(patient_panel):
    print "Alternate Admission"
    with NewAdmissionDialog(patient_panel, patient_panel.session, patient=patient_panel.patient) as dlg:
        dlg.SetTitle("New Admission for Circumcision")
        done = False
        while not done:
            dlg.ShowModal()
            if dlg.GetReturnCode() == wx.ID_OK:
                try:
                    patient = patient_panel.patient
                    doctor = dlg.get_doctor()
                    bed = dlg.get_bed()
                    problems = dlg.get_problems()
                    admission = patient.admit_circumcision(patient_panel.session, doctor, bed)
                    for problem in problems:
                        patient.problems.append(problem)
                        admission.add_problem(problem)
                except db.dbexception.AutoMODatabaseError as e:
                    patient_panel.session.rollback()
                    with wx.MessageDialog(None,
                        "Database Error Occured. {}".format(e.message),
                        "Database Error",
                        wx.OK | wx.ICON_EXCLAMATION) as err_dlg:
                        err_dlg.ShowModal()
                except Exception as e:
                    patient_panel.session.rollback()
                    with wx.MessageDialog(None,
                        "Error Occured. {}".format(e.message),
                        "Error",
                        wx.OK | wx.ICON_EXCLAMATION) as err_dlg:
                        err_dlg.ShowModal()
                else:
                    patient_panel.session.commit()
                    patient_panel.refresh()
                    event = events.PatientInfoChangedEvent(events.ID_PATIENT_INFO_CHANGED, object=patient_panel.patient)
                    wx.PostEvent(patient_panel, event)
                    done = True
            else:
                done = True


class CWardInterface(WardInterface):
    def __init__(self, parent, session=None):
        super(CWardInterface, self).__init__(parent, session)

        self.set_title("Circumcision Ward")

        self.patient_panel.admit_patient = circum_admit_patient

        self.patient_list_panel.ward_panel.print_menu.Append(ID_PRINT_ADMISSION_MULTIPLE, "Admission Sheets", "Print Admission Sheets")
        self.patient_list_panel.ward_panel.print_menu.Bind(wx.EVT_MENU, self._on_print_multiple_admission, id=ID_PRINT_ADMISSION_MULTIPLE)
        self.patient_list_panel.ward_panel.print_menu.Append(ID_PRINT_OT_NOTE, "OT Note Templates", "Print OT Note Templates")
        self.patient_list_panel.ward_panel.print_menu.Bind(wx.EVT_MENU, self._on_print_multiple_ot_note, id=ID_PRINT_OT_NOTE)


    def create_toolbar(self):
        super(CWardInterface, self).create_toolbar()
        self.toolbar.AddSeparator()
        self.toolbar.AddTool(ID_IMPORT_PATIENTS, "Batch Import Patients", images.get("new_patient_many"),
                                  wx.NullBitmap, wx.ITEM_NORMAL, "Batch Import Patients", "")


    def create_tool_menu(self):
        self.tool_menu.Append(ID_IMPORT_PATIENTS, "Import Patients", "Import Patients")
        self.Bind(wx.EVT_MENU, self._on_import, id=ID_IMPORT_PATIENTS)
        self.tool_menu.AppendSeparator()
        super(CWardInterface, self).create_tool_menu()


    def _on_import(self, event):
        with BatchPatientImporter(self, self.session) as importer:
            importer.CenterOnScreen()
            importer.ShowModal()
        self.refresh()


    def _on_print_multiple_ot_note(self, event):
        selected_beds = self.patient_list_panel.ward_panel.beds_list.get_all_selected_object()

        if not selected_beds:
            print "Nothing Selected"
            return

        admissions = []
        for bed in selected_beds:
            if bed.admission is not None:
                admissions.append(bed.admission)

        prescriptions = PyPDF2.PdfFileMerger()
        for admission in admissions:
            if admission.type == "circumcisionadmission":
                prescription = admission.generate_ot_note(self.session)
                with open(prescription,"rb") as pdf_file:
                    prescriptions.append(pdf_file)

        prescriptions_filename = tempfile.mktemp(".pdf")
        with open(prescriptions_filename,"wb") as combined_pdf:
            prescriptions.write(combined_pdf)

        pdf_view = PDFViewer(None, title="Print Preview - OT Note Templates")
        pdf_view.viewer.UsePrintDirect = ``False``
        pdf_view.viewer.LoadFile(prescriptions_filename)
        pdf_view.Show()


    def _on_print_multiple_admission(self, event):
        selected_beds = self.patient_list_panel.ward_panel.beds_list.get_all_selected_object()

        if not selected_beds:
            print "Nothing Selected"
            return

        admissions = []
        for bed in selected_beds:
            if bed.admission is not None:
                admissions.append(bed.admission)

        summaries = PyPDF2.PdfFileMerger()
        for admission in admissions:
            if admission.type == "circumcisionadmission":
                summary = admission.generate_admission_summary(self.session)
                with open(summary,"rb") as pdf_file:
                    summaries.append(pdf_file)

        summaries_filename = tempfile.mktemp(".pdf")
        with open(summaries_filename,"wb") as combined_pdf:
            summaries.write(combined_pdf)

        pdf_view = PDFViewer(None, title="Print Preview - Admission Sheets")
        pdf_view.viewer.UsePrintDirect = ``False``
        pdf_view.viewer.LoadFile(summaries_filename)
        pdf_view.Show()


    def new_admission(self):
        with NewAdmissionDialog(self, self.session) as dlg:
            done = False
            while not done:
                dlg.ShowModal()
                if dlg.GetReturnCode() == wx.ID_OK:
                    try:
                        patient = dlg.get_patient()
                        if not patient in self.session:
                            self.session.add(patient)
                        doctor = dlg.get_doctor()
                        bed = dlg.get_bed()
                        problems = dlg.get_problems()
                        admission = patient.admit_circumcision(self.session, doctor, bed)
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
                        event = events.PatientSelectedEvent(events.ID_PATIENT_SELECTED, object=patient)
                        wx.PostEvent(self, event)
                        self.patient_list_panel.refresh_all()
                        done = True
                else:
                    done = True

