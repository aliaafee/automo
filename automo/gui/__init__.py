"""WxPython Based Graphical User Interface"""
import wx

from .baseinterface import BaseInterface
from .shellinterface import ShellInterface
from .wardinterface import WardInterface
from .cwardinterface import CWardInterface


class AutoMOApp(wx.App):
    """The Main wx App Object"""
    def __init__(self, interface, parent=None):
        self.interface = interface
        self.main_frame = None
        wx.App.__init__(self, parent)


    def OnInit(self):
        """Initializes the App"""
        if self.interface == 'gui-shell':
            self.main_frame = ShellInterface(None)
        elif self.interface == 'gui-ward':
            self.main_frame = WardInterface(None)
        elif self.interface == 'gui-cward':
            self.main_frame = CWardInterface(None)
        else:
            return False

        self.main_frame.Show()
        return True
