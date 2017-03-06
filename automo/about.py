"""
The About Dialog
"""
import wx
from wx.lib.wordwrap import wordwrap
import wx.lib.agw.hyperlink as hl

from images import bitmap_from_base64, icon_robot_b64

class AboutDlg(wx.Dialog):
    """
    The About Dialog
    """
    def __init__(self, parent):
        super(AboutDlg, self).__init__(parent, wx.ID_ANY, title="About", size=(300, 360))

        image = bitmap_from_base64(icon_robot_b64)

        name = 'Auto MO'
        description = wordwrap(
            "Program to automate the tedious job of hand writing prescriptions everyday."
            "",
            250, wx.ClientDC(self))
        version = "0.1"
        website = "https://github.com/aliaafee/automo"
        copyrights = "(C) 2017 Ali Aafee"

        sizer = wx.BoxSizer(wx.VERTICAL)

        ctrl = wx.StaticText(self, label=name+" "+version, size=wx.Size(-1, -1))
        ctrl.SetFont(wx.Font(18, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.BOLD))
        sizer.Add(ctrl, 0, wx.ALIGN_CENTER | wx.TOP, border=20)

        ctrl = wx.StaticBitmap(self, 1, image, (10, 5), (image.GetWidth(), image.GetHeight()))
        sizer.Add(ctrl, 0, wx.ALIGN_CENTER | wx.ALL, border=10)

        ctrl = wx.StaticText(self, label=description, size=wx.Size(-1, -1))
        sizer.Add(ctrl, 0, wx.ALIGN_CENTER | wx.ALL, border=10)

        ctrl = hl.HyperLinkCtrl(self, -1, website, URL=website)
        sizer.Add(ctrl, 0, wx.ALIGN_CENTER | wx.ALL, border=10)

        ctrl = wx.StaticText(self, label=copyrights, size=wx.Size(-1, -1))
        sizer.Add(ctrl, 0, wx.ALIGN_CENTER | wx.ALL, border=10)

        self.SetSizer(sizer)
