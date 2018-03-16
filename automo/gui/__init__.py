"""WxPython Based Graphical User Interface"""
import sys
import traceback
import wx

from . import guiconfig
from . import configloader
from .login import LoginDlg
from . import interfaces


class AutoMOApp(wx.App):
    """The Main wx App Object"""
    def __init__(self, parent=None):
        self.interface = ""
        self.main_frame = None
        wx.App.__init__(self, parent)


    def OnInit(self):
        """Initializes the App"""
        sys.excepthook = self.exception_handler

        configloader.load_config()

        self.interface = guiconfig.STARTUP_INTERFACE
        MainFrame = interfaces.get_by_name(self.interface)

        if MainFrame is None:
            with LoginDlg(None) as logindlg:
                logindlg.CenterOnScreen()
                if logindlg.ShowModal() == wx.ID_OK:
                    interface = logindlg.get_interface()
                    if interface is not None:
                        guiconfig.STARTUP_INTERFACE = interface
                        self.interface = guiconfig.STARTUP_INTERFACE
                        MainFrame = interfaces.get_by_name(self.interface)
                else:
                    return False

        self.main_frame = MainFrame(None)
        self.main_frame.Bind(wx.EVT_CLOSE, self._on_main_frame_close)
        self.main_frame.Show()

        return True


    def exception_handler(self, type, value, trace_back):
        error_msg = "And unexpected error has occured.\n\n{}"
        traceback_str = ''.join(traceback.format_exception(type, value, trace_back))

        with wx.MessageDialog(None,error_msg.format(traceback_str), "Unexpected Error",
                              wx.OK | wx.ICON_ERROR) as dlg:
            dlg.ShowModal()
            dlg.Destroy()
        sys.exit()


    def _on_main_frame_close(self, event):
        configloader.save_config()

        event.Skip(True)
