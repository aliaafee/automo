"""Mainframe of App"""
import wx
import wx.aui

import database as db
import images
from patientlistpanel import PatientListPanel
from patientpanel import PatientPanel
from about import AboutDlg
from shell import AutoMOShell


class MainFrame(wx.Frame):
    """MainFrame of App"""
    def __init__(self, parent):
        wx.Frame.__init__(
            self,
            title='Auto MO',
            parent=parent,
            style=wx.DEFAULT_FRAME_STYLE,
            size=wx.Size(800, 600)
            )

        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(images.get('icon_16'))
        self.SetIcon(_icon)

        self.session = db.Session()

        self._init_ctrls()
        self._init_menu()


    def _init_menu(self):
        self.menu_bar = wx.MenuBar()

        self.SetMenuBar(self.menu_bar)

        self.filemenu = wx.Menu()

        #File Menu Items here
        self.filemenu.AppendSeparator()

        self.filemenu.Append(wx.ID_EXIT, "Exit", "Exit the program")
        wx.EVT_MENU(self, wx.ID_EXIT, self._on_exit)

        self.menu_bar.Append(self.filemenu, "&File")

        tool_menu = wx.Menu()
        tool_menu.Append(wx.ID_FILE1, "Python Shell", "AutoMO Python Shell")
        wx.EVT_MENU(self, wx.ID_FILE1, self._on_python_shell)

        self.menu_bar.Append(tool_menu, "&Tools")


        help_menu = wx.Menu()

        help_menu.Append(wx.ID_ABOUT, "&About", "About this software")
        wx.EVT_MENU(self, wx.ID_ABOUT, self._on_about)

        self.menu_bar.Append(help_menu, "&Help")

        #self.status = self.CreateStatusBar()


    def _init_ctrls(self):
        #Splitter Window
        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        #left Panel
        self.patient_list_panel = PatientListPanel(splitter, self.session,
                                                   style=wx.BORDER_SUNKEN)

        #Right Panel
        self.patient_panel = PatientPanel(splitter, self.session, style=wx.BORDER_SUNKEN)

        #Introduce each other
        self.patient_list_panel.patient_panel = self.patient_panel
        #self.patient_panel.patient_list_panel = self.patient_list_panel

        #Split Windows
        splitter.SplitVertically(self.patient_list_panel, self.patient_panel)
        splitter.SetMinimumPaneSize(100)
        splitter.SetSashPosition(250)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splitter, 1, wx.ALL | wx.EXPAND)
        self.SetSizer(sizer)

        self.Layout()


    def _on_python_shell(self, event):
        with AutoMOShell(self, self.session) as dlg:
            dlg.ShowModal()


    def  _on_about(self, event):
        """ Open About Dialog """
        with AboutDlg(self) as about_dlg:
            about_dlg.CenterOnParent()
            about_dlg.ShowModal()


    def _on_exit(self, event):
        """ Exit the App """
        self.Close()
