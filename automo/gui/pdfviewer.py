"""PDF Viewer"""
import wx
import wx.lib.sized_controls as sc
import wx.lib.pdfviewer
#from wx.lib.pdfviewer import pdfViewer, pdfButtonPanel

from . import images

wx.lib.pdfviewer.viewer.VERBOSE = False


class PDFViewer(sc.SizedFrame):
    """PDF Viewer"""
    def __init__(self, parent, **kwds):
        super(PDFViewer, self).__init__(parent, **kwds)

        _icon = wx.Icon()
        _icon.CopyFromBitmap(images.get('icon_16'))
        self.SetIcon(_icon)

        pane_cont = self.GetContentsPane()
        self.buttonpanel = wx.lib.pdfviewer.pdfButtonPanel(pane_cont, wx.NewId(),
                                          wx.DefaultPosition, wx.DefaultSize, 0)
        self.buttonpanel.SetSizerProps(expand=True)
        self.viewer = wx.lib.pdfviewer.pdfViewer(pane_cont, wx.NewId(), wx.DefaultPosition,
                                wx.DefaultSize,
                                wx.HSCROLL|wx.VSCROLL|wx.SUNKEN_BORDER)
        self.viewer.UsePrintDirect = False
        self.viewer.SetSizerProps(expand=True, proportion=1)


        self.buttonpanel.viewer = self.viewer
        self.viewer.buttonpanel = self.buttonpanel
