"""Discharge Interface"""
import wx
import wx.lib.pdfviewer

from . import images

wx.lib.pdfviewer.viewer.VERBOSE = False


class DischargePanel(wx.Panel):
    """Patient Search Panel"""
    def __init__(self, parent, session, **kwds):
        super(DischargePanel, self).__init__(parent, **kwds)

        self.session = session

        #self.buttonpanel = wx.lib.pdfviewer.pdfButtonPanel(self, wx.NewId(),
        #                                  wx.DefaultPosition, wx.DefaultSize, 0)

        self.viewer = wx.lib.pdfviewer.pdfViewer(self, wx.NewId(), wx.DefaultPosition,
                                wx.DefaultSize,
                                wx.HSCROLL|wx.VSCROLL|wx.BORDER_NONE)
        self.viewer.UsePrintDirect = False

        sizer = wx.BoxSizer(wx.VERTICAL)

        #sizer.Add(self.buttonpanel, 0 , wx.EXPAND)
        sizer.Add(self.viewer, 1 , wx.EXPAND)

        #self.buttonpanel.viewer = self.viewer
        #self.viewer.buttonpanel = self.buttonpanel

        self.SetSizer(sizer)


    def refresh(self):
        pass


    def set_admission(self, admission):
        filename = admission.generate_discharge_summary(self.session)

        self.viewer.LoadFile(filename)
        self.viewer.SetZoom(1.0)

