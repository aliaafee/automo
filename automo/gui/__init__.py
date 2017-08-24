"""WxPython Based Graphical User Interface"""
import wx

from .baseinterface import BaseInterface
from .shellinterface import ShellInterface
from .wardinterface import WardInterface


class AutoMOApp(wx.App):
    """The Main wx App Object"""
    def __init__(self, parent=None):
        self.main_frame = None
        wx.App.__init__(self, parent)


    def OnInit(self):
        """Initializes the App"""
        self.main_frame = WardInterface(None)
        self.main_frame.Show()
        return True
