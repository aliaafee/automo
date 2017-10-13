"""Ward Interface"""
import wx
import wx.py

from .. import database as db
from . import events
from . import images
from .baseinterface import BaseInterface
from .shellinterface import ShellInterface
from .patientlistpanel import PatientListPanel
from .patientpanel import PatientPanel
from .patientinfo import PatientForm
from .newadmission import NewAdmissionDialog

ID_NEW_PATIENT = wx.NewId()
ID_NEW_ADMISSION = wx.NewId()
ID_SHELL = wx.NewId()


class WardInterface(BaseInterface):
    """Ward Interface"""
    def __init__(self, parent, session=None):
        super(WardInterface, self).__init__(parent, session)

        self.set_title("Ward")

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)
        self.create_toolbar()
        self.toolbar.Realize()

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self.patient_list_panel = PatientListPanel(splitter, self.session, style=wx.BORDER_THEME)

        self.patient_panel = PatientPanel(splitter, self.session, style=wx.BORDER_THEME)
        self.patient_panel.Bind(events.EVT_AM_PATIENT_INFO_CHANGED, self._on_patient_info_changed)

        splitter.SplitVertically(self.patient_list_panel, self.patient_panel)
        splitter.SetMinimumPaneSize(5)
        splitter.SetSashPosition(250)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolbar, 0, wx.EXPAND)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Bind(events.EVT_AM_PATIENT_SELECTED, self._on_patient_selected)

        self.Layout()


    def create_toolbar(self):
        self.toolbar.AddTool(wx.ID_REFRESH, "Refresh", images.get("refresh_24"),
                                  wx.NullBitmap, wx.ITEM_NORMAL, "Refresh", "")
        self.toolbar.AddSeparator()
        self.toolbar.AddTool(ID_NEW_PATIENT, "New Patient", images.get("new_patient"),
                                  wx.NullBitmap, wx.ITEM_NORMAL, "New Patient", "")
        self.toolbar.AddTool(ID_NEW_ADMISSION, "New Admission", images.get("admit"),
                                  wx.NullBitmap, wx.ITEM_NORMAL, "New Admission", "")

        self.toolbar.Bind(wx.EVT_TOOL, self._on_refresh, id=wx.ID_REFRESH)


    def create_file_menu(self):
        self.file_menu.Append(ID_NEW_PATIENT, "New Patient", "Create New Patient")
        self.file_menu.Append(ID_NEW_ADMISSION, "New Admission", "Create New Admission")
        self.file_menu.AppendSeparator()

        self.Bind(wx.EVT_MENU, self._on_new_patient, id=ID_NEW_PATIENT)
        self.Bind(wx.EVT_MENU, self._on_new_admission, id=ID_NEW_ADMISSION)

        super(WardInterface, self).create_file_menu()


    def create_tool_menu(self):
        super(WardInterface, self).create_tool_menu()
        self.tool_menu.Append(ID_SHELL, "Python Shell", "AutoMO Python Shell")
        self.Bind(wx.EVT_MENU, self._on_python_shell, id=ID_SHELL)


    def refresh(self):
        super(WardInterface, self).refresh()
        self.patient_list_panel.refresh()
        self.patient_panel.refresh()


    def _on_new_patient(self, event):
        with PatientForm(self, title="New Patient") as editor:
            editor.CenterOnParent()
            done = False
            while not done:
                if editor.ShowModal() == wx.ID_OK:
                    try:
                        new_patient = editor.get_object()
                        self.session.add(new_patient)
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
                        event = events.PatientSelectedEvent(events.ID_PATIENT_SELECTED, object=new_patient)
                        wx.PostEvent(self, event)
                        done = True
                else:
                    done = True


    def _on_new_admission(self, event):
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
                        event = events.PatientSelectedEvent(events.ID_PATIENT_SELECTED, object=patient)
                        wx.PostEvent(self, event)
                        self.patient_list_panel.refresh_all()
                        done = True
                else:
                    done = True
                


    def _on_refresh(self, event):
        self.refresh()


    def _on_patient_info_changed(self, event):
        print "here"
        #if type(event.object) == db.Patient:
        self.patient_list_panel.refresh_all()
        #elif type(event.object) == db.Bed:
        #self.patient_list_panel.refresh_all()
        event.Skip()


    def _on_patient_selected(self, event):
        selected_patient = event.object

        if self.patient_panel.is_unsaved():
            self.patient_panel.save_changes()

        if selected_patient is None:
            self.patient_panel.unset()

        self.patient_panel.set(selected_patient)


    def _on_python_shell(self, event):
        shell = ShellInterface(self, self.session)
        shell.Show()
