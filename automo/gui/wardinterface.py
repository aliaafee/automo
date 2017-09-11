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


class WardInterface(BaseInterface):
    """Ward Interface"""
    def __init__(self, parent, session=None):
        super(WardInterface, self).__init__(parent, session)

        self.set_title("Ward")

        self.toolbar = self._get_toolbar()

        self.tool_menu.Append(wx.ID_FILE1, "Python Shell", "AutoMO Python Shell")
        wx.EVT_MENU(self, wx.ID_FILE1, self._on_python_shell)

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self.patient_list_panel = PatientListPanel(splitter, self.session, style=wx.BORDER_SUNKEN)
        self.patient_list_panel.Bind(events.EVT_AM_PATIENT_CHANGED, self._on_patient_selected)

        self.patient_panel = PatientPanel(splitter, self.session, style=wx.BORDER_SUNKEN)
        self.patient_panel.Bind(events.EVT_AM_PATIENT_INFO_CHANGED, self._on_patient_info_changed)

        splitter.SplitVertically(self.patient_list_panel, self.patient_panel)
        splitter.SetMinimumPaneSize(5)
        splitter.SetSashPosition(250)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolbar, 0, wx.EXPAND)
        sizer.Add(splitter, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Layout()


    def refresh(self):
        super(WardInterface, self).refresh()
        self.patient_list_panel.refresh()
        self.patient_panel.refresh()


    def _get_toolbar(self):
        toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)

        toolbar.AddLabelTool(wx.ID_REFRESH, "Refresh", images.get("refresh_24"),
                                  wx.NullBitmap, wx.ITEM_NORMAL, "Refresh", "")

        toolbar.AddSeparator()

        toolbar.Bind(wx.EVT_TOOL, self._on_refresh, id=wx.ID_REFRESH)

        toolbar.Realize()

        return toolbar


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
