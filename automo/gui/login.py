"""Login dialog"""
import wx

from . import guiconfig
from .interfaces import INTERFACES


class LoginDlg(wx.Dialog):
    """Login dialog"""
    def __init__(self, parent, size=wx.Size(300, 150), **kwds):
        super(LoginDlg, self).__init__(parent, size=size, **kwds)

        self.SetTitle("Automo")

        self.interface_labels = []
        self.interface_names = []
        for name, (label, interface_class) in INTERFACES.items():
            self.interface_labels.append(label)
            self.interface_names.append(name)

        self.interface = guiconfig.STARTUP_INTERFACE
        self.main_frame = None

        btn_login = wx.Button(self, label="Start")
        btn_login.Bind(wx.EVT_BUTTON, self._on_login)

        btn_cancel= wx.Button(self, label="Cancel")
        btn_cancel.Bind(wx.EVT_BUTTON, self._on_cancel)

        lbl_interface = wx.StaticText(self, label="Interface")
        self.choice_interface = wx.Choice(self)
        self.choice_interface.AppendItems(self.interface_labels)
        print guiconfig.STARTUP_INTERFACE
        if self.interface in self.interface_names:
            index = self.interface_names.index(self.interface)
            self.choice_interface.SetSelection(index)

        grid_sizer = wx.FlexGridSizer(1,2, 10, 10)
        grid_sizer.Add(lbl_interface, 1, wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.AddGrowableCol(1)
        grid_sizer.Add(self.choice_interface, 1, wx.EXPAND)

        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(btn_login, 1, wx.EXPAND | wx.RIGHT, border=5)
        btn_sizer.Add(btn_cancel, 1, wx.EXPAND | wx.LEFT, border=5)


        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(grid_sizer, 0, wx.EXPAND | wx.ALL, border=10)
        sizer.AddStretchSpacer()
        sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, border=10)

        self.SetSizer(sizer)


    def get_interface(self):
        sel_index = self.choice_interface.GetSelection()
        if sel_index >= 0:
            self.interface = self.interface_names[sel_index]
            return self.interface


    def _on_login(self, event):
        self.EndModal(wx.ID_OK)

    
    def _on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)
