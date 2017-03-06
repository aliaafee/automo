"""
Mainframe of App
"""
import wx
import wx.aui

from database import Session, Drug, Diagnosis
from images import bitmap_from_base64, icon_16_b64
from patientlistpanel import PatientListPanel
from patientpanel import PatientPanel
from about import AboutDlg
from historyeditor import HistoryEditor


class MainFrame(wx.Frame):
    """
    MainFrame of App
    """
    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            title='Auto MO',
            parent=parent,
            style=wx.DEFAULT_FRAME_STYLE,
            size=wx.Size(800, 600)
            )

        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(bitmap_from_base64(icon_16_b64))
        self.SetIcon(_icon)

        self.session = Session()

        self.patients = []
        self.selected_patient = None

        self._init_ctrls()
        self._init_menu()

        self.patient_list_panel.UpdateList()


    def _init_menu(self):
        self.menu_bar = wx.MenuBar()

        self.SetMenuBar(self.menu_bar)

        self.filemenu = wx.Menu()

        menu_id = 400
        self.filemenu.Append(menu_id, "Print Prescription", "Print this prescription.")
        wx.EVT_MENU(self, menu_id, self.patient_panel.OnPrint)

        menu_id = 401
        self.filemenu.Append(menu_id, "Print All Prescriptions", "Print all prescriptions.")
        wx.EVT_MENU(self, menu_id, self.patient_list_panel.OnPrintAll)

        menu_id = 402
        self.filemenu.Append(menu_id, "Print Prescriptions List", "Print prescriptions list.")
        wx.EVT_MENU(self, menu_id, self.patient_list_panel.OnPrintList)

        menu_id = 403
        self.filemenu.Append(menu_id, "Print Census List", "Print Census list.")
        wx.EVT_MENU(self, menu_id, self.patient_list_panel.OnPrintCensusList)

        self.filemenu.AppendSeparator()

        self.filemenu.Append(wx.ID_EXIT, "Exit", "Exit the program")
        wx.EVT_MENU(self, wx.ID_EXIT, self.OnExit)

        self.menu_bar.Append(self.filemenu, "&File")

        tool_menu = wx.Menu()

        menu_id = 404
        tool_menu.Append(menu_id, "Edit Drug History", "Edit Drug History")
        wx.EVT_MENU(self, menu_id, self.OnDrugHistory)

        menu_id = 405
        tool_menu.Append(menu_id, "Edit Diagnosis History", "Edit Diagnosis History")
        wx.EVT_MENU(self, menu_id, self.OnDiagnosisHistory)

        self.menu_bar.Append(tool_menu, "&Tools")

        help_menu = wx.Menu()

        menu_id = 406
        help_menu.Append(menu_id, "&About", "About this software")
        wx.EVT_MENU(self, menu_id, self.OnAboutDlg)

        self.menu_bar.Append(help_menu, "&Help")

        self.status = self.CreateStatusBar()


    def _init_ctrls(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        #Splitter Window
        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE | wx.SP_3D)

        #left Panel
        self.patient_list_panel = PatientListPanel(splitter, self.session, size=wx.Size(300, -1))

        #Right Panel
        self.patient_panel = PatientPanel(splitter, self.session)

        #Introduce each other
        self.patient_list_panel.patient_panel = self.patient_panel
        self.patient_panel.patient_list_panel = self.patient_list_panel

        #Split Windows
        splitter.SplitVertically(self.patient_list_panel, self.patient_panel)
        splitter.SetMinimumPaneSize(100)

        sizer.Add(splitter, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)

        self.Layout()


    def OnDrugHistory(self, event):
        """ Open Drug History Editor """
        editor_dlg = HistoryEditor(self, self.session, Drug, title="Drug History")

        editor_dlg.ShowModal()


    def OnDiagnosisHistory(self, event):
        """ Opend Diagnosis History Editor """
        editor_dlg = HistoryEditor(self, self.session, Diagnosis, title="Diagnosis History")

        editor_dlg.ShowModal()


    def OnAboutDlg(self, event):
        """ Open About Dialog """
        about_dlg = AboutDlg(None)
        about_dlg.Show()


    def OnExit(self, event):
        """ Exit the App """
        self.Close()
