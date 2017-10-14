"""C Ward Interface"""
import wx

from .. import database as db
from . import events
from . import images
from .wardinterface import WardInterface
from .batchpatientimporter import BatchPatientImporter
from .newadmission import NewAdmissionDialog

ID_IMPORT_PATIENTS = wx.NewId()


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

