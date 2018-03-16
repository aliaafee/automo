"""Base for all Wizard Pages"""
import wx


class BasePage(wx.adv.WizardPage):
    """Base for all Wizard Pages"""
    def __init__(self, parent, session, title=""):
        super(BasePage, self).__init__(parent)
        self.next = self.prev = None
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label=title)
        title.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.sizer.Add(title, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        self.SetSizer(self.sizer)
        self.session = session
        self.error_message = "Error"

    def is_valid(self):
        return True

    def show_error(self):
        with wx.MessageDialog(None,
                              self.error_message,
                              "Error",
                              wx.OK | wx.ICON_EXCLAMATION) as dlg:
            dlg.ShowModal()

    def set(self):
        pass

    def must_skip(self):
        return False

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next

    def GetPrev(self):
        return self.prev
