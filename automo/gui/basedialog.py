"""Base of commonly used dialogs"""
import wx


class BaseDialog(wx.Dialog):
    """Base of commonly used dialogs"""
    def __init__(self, parent, **kwds):
        super(BaseDialog, self).__init__(
                parent, style=wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION,
                **kwds)

        self.button_ok = wx.Button(self, label="OK", size=(100, -1))
        self.button_ok.Bind(wx.EVT_BUTTON, self.on_ok)

        self.button_cancel = wx.Button(self, label="Cancel")
        self.button_cancel.Bind(wx.EVT_BUTTON, self.on_cancel)

        self.content_sizer = wx.BoxSizer(wx.VERTICAL)
        self.footer_sizer = wx.BoxSizer(wx.VERTICAL)


    def setup_sizers(self):
        """Setup Sizer"""
        self.setup_contents()
        self.setup_footer()

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.content_sizer, 1, wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.footer_sizer, 0, wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=5)
        self.SetSizer(sizer)


    def setup_contents(self):
        """Add Contents to conten_sizer"""
        pass


    def setup_footer(self):
        """Add Contents to footer_sizer"""
        self.footer_sizer.Add(self.button_ok, 0, wx.EXPAND | wx.ALL, border=5)
        self.footer_sizer.Add(self.button_cancel, 0, wx.EXPAND | wx.ALL, border=5)
        

    def on_ok(self, event):
        """OK button pressed"""
        self.EndModal(wx.ID_OK)


    def on_cancel(self, event):
        """Cancel button pressed"""
        self.EndModal(wx.ID_CANCEL)
