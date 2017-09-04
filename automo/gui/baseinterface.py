"""Ward Interface"""
import wx

from .. import database as db
from . import images
from .about import AboutDlg


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

        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(images.get('icon_16'))
        self.SetIcon(_icon)

        if session is None:
            self.session = db.Session()
        else:
            self.session = session

        self.menu_bar = wx.MenuBar()

        self.SetMenuBar(self.menu_bar)

        self.filemenu = wx.Menu()
        self.menu_bar.Append(self.filemenu, "&File")
        self.filemenu.AppendSeparator()
        self.filemenu.Append(wx.ID_EXIT, "Exit", "Exit the program")
        wx.EVT_MENU(self, wx.ID_EXIT, self._on_exit)

        self.print_menu = wx.Menu()
        self.menu_bar.Append(self.print_menu, "&Print")

        self.tool_menu = wx.Menu()
        self.menu_bar.Append(self.tool_menu, "&Tools")

        self.help_menu = wx.Menu()
        self.menu_bar.Append(self.help_menu, "&Help")
        self.help_menu.Append(wx.ID_ABOUT, "&About", "About this software")
        wx.EVT_MENU(self, wx.ID_ABOUT, self._on_about)


    def set_title(self, title):
        """Set the window title"""
        self.SetTitle("AutoMO - {}".format(title))


    def  _on_about(self, event):
        """ Open About Dialog """
        with AboutDlg(self) as about_dlg:
            about_dlg.CenterOnParent()
            about_dlg.ShowModal()


    def _on_exit(self, event):
        """ Exit the App """
        self.Close()
        self.Destroy()
        