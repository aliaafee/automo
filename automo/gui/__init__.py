"""WxPython Based Graphical User Interface"""
import sys
import traceback
import wx

from . import guiconfig
from .login import LoginDlg
from .baseinterface import BaseInterface
from .shellinterface import ShellInterface
from .wardinterface import WardInterface
from .cwardinterface import CWardInterface
from .dischargeinterface import DischargeInterface

INTERFACES = {
    'gui-shell' : ShellInterface,
    'gui-ward' : WardInterface,
    'gui-cward' : CWardInterface,
    'gui-discharge' : DischargeInterface
}


class AutoMOApp(wx.App):
    """The Main wx App Object"""
    def __init__(self, parent=None):
        self.interface = ""
        self.main_frame = None
        wx.App.__init__(self, parent)


    def OnInit(self):
        """Initializes the App"""
        sys.excepthook = self.exception_handler

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

        MainFrame = INTERFACES[self.interface]

        self.main_frame = MainFrame(None)
        self.main_frame.Bind(wx.EVT_CLOSE, self._on_main_frame_close)
        self.main_frame.Show()

        return True


    def exception_handler(self, type, value, trace_back):
        error_msg = "And unexpected error has occured, AutoMO will close.\n\n{}"
        traceback_str = ''.join(traceback.format_exception(type, value, trace_back))

        with wx.MessageDialog(None,error_msg.format(traceback_str), "Fatal Error",
                              wx.OK | wx.ICON_ERROR) as dlg:
            dlg.ShowModal()
            dlg.Destroy()
        sys.exit()


    def _on_main_frame_close(self, event):
        guiconfig.save_config()

        event.Skip(True)
