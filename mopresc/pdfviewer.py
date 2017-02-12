import wx
import wx.lib.sized_controls as sc
from wx.lib.pdfviewer import pdfViewer, pdfButtonPanel

from images import *


class PDFViewer(sc.SizedFrame):
    def __init__(self, parent, **kwds):
        super(PDFViewer, self).__init__(parent, **kwds)

        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(BitmapFromBase64(icon_16_b64))
        self.SetIcon(_icon)

        paneCont = self.GetContentsPane()
        self.buttonpanel = pdfButtonPanel(paneCont, wx.NewId(),
                                wx.DefaultPosition, wx.DefaultSize, 0)
        self.buttonpanel.SetSizerProps(expand=True)
        self.viewer = pdfViewer(paneCont, wx.NewId(), wx.DefaultPosition,
                                wx.DefaultSize,
                                wx.HSCROLL|wx.VSCROLL|wx.SUNKEN_BORDER)
        self.viewer.UsePrintDirect = ``False``
        self.viewer.SetSizerProps(expand=True, proportion=1)

        self.buttonpanel.viewer = self.viewer
        self.viewer.buttonpanel = self.buttonpanel
