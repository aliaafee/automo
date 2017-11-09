"""Ward Interface"""
import wx

from .. import database as db
from . import images
from .about import AboutDlg
from .settingsdialog import SettingsDialog


ID_SETTINGS = wx.NewId()


class BaseInterface(wx.Frame):
    """Basis for other interfaces"""
    def __init__(self, parent, session=None):
        wx.Frame.__init__(
            self,
            title='Auto MO',
            parent=parent,
            style=wx.DEFAULT_FRAME_STYLE,
            size=wx.Size(800, 600)
            )

        _icon = wx.Icon()
        _icon.CopyFromBitmap(images.get('icon_16'))
        self.SetIcon(_icon)

        if session is None:
            self.session = db.Session()
        else:
            self.session = session

        self.menu_bar = wx.MenuBar()

        self.SetMenuBar(self.menu_bar)

        self.file_menu = wx.Menu()
        self.menu_bar.Append(self.file_menu, "&File")

        #self.print_menu = wx.Menu()
        #self.menu_bar.Append(self.print_menu, "&Print")

        self.tool_menu = wx.Menu()
        self.menu_bar.Append(self.tool_menu, "&Tools")

        self.help_menu = wx.Menu()
        self.menu_bar.Append(self.help_menu, "&Help")

        self.create_file_menu()
        self.create_tool_menu()
        self.create_help_menu()


    def create_file_menu(self):
        self.file_menu.Append(wx.ID_EXIT, "Exit", "Exit the program")
        self.Bind(wx.EVT_MENU, self._on_exit, id=wx.ID_EXIT)


    def create_tool_menu(self):
        self.tool_menu.Append(ID_SETTINGS, "Settings", "Edit Settings")
        self.Bind(wx.EVT_MENU, self._on_settings, id=ID_SETTINGS)


    def create_help_menu(self):
        self.help_menu.Append(wx.ID_ABOUT, "&About", "About this software")
        self.Bind(wx.EVT_MENU, self._on_about, id=wx.ID_ABOUT)


    def refresh(self):
        self.session.commit()


    def set_title(self, title):
        """Set the window title"""
        self.SetTitle("AutoMO - {}".format(title))


    def _on_settings(self, event):
        """AutoMO Settings"""
        with SettingsDialog(self, self.session) as dlg:
            dlg.CenterOnParent()
            dlg.ShowModal()


    def  _on_about(self, event):
        """ Open About Dialog """
        with AboutDlg(self) as about_dlg:
            about_dlg.CenterOnParent()
            about_dlg.ShowModal()


    def _on_exit(self, event):
        """ Exit the App """
        self.Close()
        self.Destroy()
        