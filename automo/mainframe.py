import wx
import wx.aui

from database import Session, Drug, Diagnosis
from images import *
from patientlistpanel import PatientListPanel
from patientpanel import PatientPanel
from about import AboutDlg
from historyeditor import HistoryEditor


class MainFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            title = 'Auto MO',
            parent = parent,
            style = wx.DEFAULT_FRAME_STYLE,
            size = wx.Size(800, 600)
            )

        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(BitmapFromBase64(icon_16_b64))
        self.SetIcon(_icon)

        self.session = Session()

        self.Patients = []
        self.SelectedPatient = None
        
        self._InitCtrls()
        self._InitMenu()

        self.patientListPanel.UpdateList()


    def _InitMenu(self):
        self.menuBar = wx.MenuBar()

        self.SetMenuBar(self.menuBar)

        self.filemenu = wx.Menu()

        id = 400
        self.filemenu.Append(id, "Print Prescription", "Print this prescription.")
        wx.EVT_MENU(self, id,  self.patientPanel.OnPrint)

        id = 401
        self.filemenu.Append(id, "Print All Prescriptions", "Print all prescriptions.")
        wx.EVT_MENU(self, id,  self.patientListPanel.OnPrintAll)

        id = 402
        self.filemenu.Append(id, "Print Prescriptions List", "Print prescriptions list.")
        wx.EVT_MENU(self, id,  self.patientListPanel.OnPrintList)

        id = 403
        self.filemenu.Append(id, "Print Census List", "Print Census list.")
        wx.EVT_MENU(self, id,  self.patientListPanel.OnPrintCensusList)

        self.filemenu.AppendSeparator()

        self.filemenu.Append(wx.ID_EXIT, "Exit", "Exit the program")
        wx.EVT_MENU(self, wx.ID_EXIT,  self.OnExit)

        self.menuBar.Append(self.filemenu, "&File")

        toolMenu = wx.Menu()

        id = 404
        about_menu_item = toolMenu.Append(id, "Edit Drug History", "Edit Drug History")
        wx.EVT_MENU(self, id, self.OnDrugHistory)

        id = 405
        about_menu_item = toolMenu.Append(id, "Edit Diagnosis History", "Edit Diagnosis History")
        wx.EVT_MENU(self, id, self.OnDiagnosisHistory)
        
        self.menuBar.Append(toolMenu, "&Tools")

        helpMenu = wx.Menu()

        id = 406
        about_menu_item = helpMenu.Append(id, "&About", "About this software")
        wx.EVT_MENU(self, id, self.OnAboutDlg)
        
        self.menuBar.Append(helpMenu, "&Help")

        self.status = self.CreateStatusBar()


    def _InitCtrls(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        #Splitter Window
        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE | wx.SP_3D)

        #left Panel
        self.patientListPanel = PatientListPanel(splitter, self.session, size=wx.Size(300,-1))

        #Right Panel
        self.patientPanel = PatientPanel(splitter, self.session)

        #Introduce each other
        self.patientListPanel.patientPanel = self.patientPanel
        self.patientPanel.patientListPanel = self.patientListPanel

        #Split Windows
        splitter.SplitVertically(self.patientListPanel, self.patientPanel)
        splitter.SetMinimumPaneSize(100)

        sizer.Add(splitter, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)

        self.Layout()


    def OnDrugHistory(self, event):
        editorDlg = HistoryEditor(self, self.session, Drug, title="Drug History")

        editorDlg.ShowModal()


    def OnDiagnosisHistory(self, event):
        editorDlg = HistoryEditor(self, self.session, Diagnosis, title="Diagnosis History")

        editorDlg.ShowModal()


    def OnAboutDlg(self, event):
        aboutDlg = AboutDlg(None)
        aboutDlg.Show()


    def OnExit(self, event):
        self.Close()
