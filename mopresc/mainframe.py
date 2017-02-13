import wx
import wx.aui

from database import Session
from images import *
from patientlistpanel import PatientListPanel
from patientpanel import PatientPanel
from about import AboutDlg


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
        self.filemenu.Append(id, "Print", "Print this prescription.")
        wx.EVT_MENU(self, id,  self.patientPanel.OnPrint)

        id = 401
        self.filemenu.Append(id, "Print All", "Print all prescriptions.")
        wx.EVT_MENU(self, id,  self.patientListPanel.OnPrintAll)


        self.filemenu.Append(wx.ID_EXIT, "Exit", "Exit the program")
        wx.EVT_MENU(self, wx.ID_EXIT,  self.OnExit)

        self.menuBar.Append(self.filemenu, "&File")

        helpMenu = wx.Menu()

        id = 402
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


    def OnAboutDlg(self, event):
        aboutDlg = AboutDlg(None)
        aboutDlg.Show()


    def OnExit(self, event):
        self.Close()
