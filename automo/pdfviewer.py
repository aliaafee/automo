"""
PDF Viewer
"""
import wx
import wx.lib.sized_controls as sc
from wx.lib.pdfviewer import pdfViewer, pdfButtonPanel

from images import bitmap_from_base64, icon_16_b64


class PDFViewer(sc.SizedFrame):
    """
    PDF Viewer
    """
    def __init__(self, parent, **kwds):
        super(PDFViewer, self).__init__(parent, **kwds)

        _icon = wx.EmptyIcon()
        _icon.CopyFromBitmap(bitmap_from_base64(icon_16_b64))
        self.SetIcon(_icon)

        pane_cont = self.GetContentsPane()
        self.buttonpanel = pdfButtonPanel(pane_cont, wx.NewId(),
                                          wx.DefaultPosition, wx.DefaultSize, 0)
        self.buttonpanel.SetSizerProps(expand=True)
        self.viewer = pdfViewer(pane_cont, wx.NewId(), wx.DefaultPosition,
                                wx.DefaultSize,
                                wx.HSCROLL|wx.VSCROLL|wx.SUNKEN_BORDER)
        self.viewer.UsePrintDirect = ``False``
        self.viewer.SetSizerProps(expand=True, proportion=1)

        self.buttonpanel.viewer = self.viewer
        self.viewer.buttonpanel = self.buttonpanel
