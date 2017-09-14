"""WxPython Based Graphical User Interface"""
import wx

from . import guiconfig
from .login import LoginDlg
from .baseinterface import BaseInterface
from .shellinterface import ShellInterface
from .wardinterface import WardInterface
from .cwardinterface import CWardInterface


class AutoMOApp(wx.App):
    """The Main wx App Object"""
    def __init__(self, parent=None):
        self.interface = ""
        self.main_frame = None
        wx.App.__init__(self, parent)


    def OnInit(self):
        """Initializes the App"""
        guiconfig.load_config()

        self.interface = guiconfig.STARTUP_INTERFACE

        if self.interface == "":
            with LoginDlg(None) as logindlg:
                logindlg.CenterOnScreen()
                if logindlg.ShowModal() == wx.ID_OK:
                    interface = logindlg.get_interface()
                    print interface
                    if interface is not None:
                        guiconfig.STARTUP_INTERFACE = interface
                        self.interface = guiconfig.STARTUP_INTERFACE
                else:
                    return False

        if self.interface == 'gui-shell':
            self.main_frame = ShellInterface(None)
        elif self.interface == 'gui-ward':
            self.main_frame = WardInterface(None)
        elif self.interface == 'gui-cward':
            self.main_frame = CWardInterface(None)
        else:
            return False

        self.main_frame.Bind(wx.EVT_CLOSE, self._on_main_frame_close)
        self.main_frame.Show()
        return True


    def _on_main_frame_close(self, event):
        guiconfig.save_config()

        event.Skip(True)
