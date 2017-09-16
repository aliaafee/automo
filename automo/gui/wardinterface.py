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
        self.toolbar.AddLabelTool(wx.ID_REFRESH, "Refresh", images.get("refresh_24"),
                                  wx.NullBitmap, wx.ITEM_NORMAL, "Refresh", "")

        self.toolbar.Bind(wx.EVT_TOOL, self._on_refresh, id=wx.ID_REFRESH)


    def create_file_menu(self):
        self.file_menu.Append(ID_NEW_PATIENT, "New Patient", "Create New Patient")
        self.file_menu.Append(ID_NEW_PATIENT, "New Admission", "Create New Admission")
        self.file_menu.AppendSeparator()

        wx.EVT_MENU(self, ID_NEW_PATIENT, self._on_new_patient)

        super(WardInterface, self).create_file_menu()


    def create_tool_menu(self):
        super(WardInterface, self).create_tool_menu()
        self.tool_menu.Append(ID_SHELL, "Python Shell", "AutoMO Python Shell")
        wx.EVT_MENU(self, ID_SHELL, self._on_python_shell)


    def refresh(self):
        super(WardInterface, self).refresh()
        self.patient_list_panel.refresh()
        self.patient_panel.refresh()


    def _on_new_patient(self, event):
        with PatientForm(self, title="New Patient") as editor:
            editor.CenterOnParent()
            if editor.ShowModal() == wx.ID_OK:
                new_patient = editor.get_object()
                self.session.add(new_patient)
                self.session.commit()
                event = events.PatientSelectedEvent(events.ID_PATIENT_SELECTED, object=new_patient)
                wx.PostEvent(self, event)


    def _on_refresh(self, event):
        self.refresh()


    def _on_patient_info_changed(self, event):
        if type(event.object) == db.Patient:
            self.patient_list_panel.refresh_selected()
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
