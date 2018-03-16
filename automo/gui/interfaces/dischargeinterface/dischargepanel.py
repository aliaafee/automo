"""Discharge Interface"""
import wx
import wx.lib.pdfviewer

from ... import images
from ...pdfviewer import PDFViewer

wx.lib.pdfviewer.viewer.VERBOSE = False

ID_PRINT_PRESCRIPTION = wx.NewId()

class DischargePanel(wx.Panel):
    """Patient Search Panel"""
    def __init__(self, parent, session, **kwds):
        super(DischargePanel, self).__init__(parent, **kwds)

        self.admission = None

        self.session = session

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER | wx.TB_HORZ_TEXT)
        self.toolbar.AddTool(wx.ID_PRINT, "Print Discharge", images.get("print_24"), wx.NullBitmap, wx.ITEM_NORMAL, "Print Discharge Summary", "")
        self.toolbar.AddTool(ID_PRINT_PRESCRIPTION, "Print Prescription", images.get("print_24"), wx.NullBitmap, wx.ITEM_NORMAL, "Print Prescription", "")
        self.toolbar.Realize()

        self.toolbar.Bind(wx.EVT_TOOL, self._on_print, id=wx.ID_PRINT)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_print_prescripion, id=ID_PRINT_PRESCRIPTION)

        self.viewer = wx.lib.pdfviewer.pdfViewer(self, wx.NewId(), wx.DefaultPosition,
                                wx.DefaultSize,
                                wx.HSCROLL|wx.VSCROLL|wx.BORDER_NONE)
        self.viewer.UsePrintDirect = False

        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(self.toolbar, 0 , wx.EXPAND)
        sizer.Add(self.viewer, 1 , wx.EXPAND)

        self.SetSizer(sizer)

        self.toolbar.Disable()


    def _on_print(self, event):
        if self.admission is None:
            return

        self.viewer.Print()


    def _on_print_prescripion(self, event):
        if self.admission is None:
            return
    
        filename = self.admission.get_prescription_pdf(self.session)

        pdf_view = PDFViewer(None, title="Print Preview - Prescription")
        pdf_view.viewer.UsePrintDirect = False
        pdf_view.viewer.LoadFile(filename)
        pdf_view.Show()


    def refresh(self):
        if self.admission is None:
            return

        filename = self.admission.generate_discharge_summary(self.session)

        self.viewer.LoadFile(filename)
        self.viewer.SetZoom(1.0)


    def set_admission(self, admission):
        self.admission = admission

        self.refresh()

        self.toolbar.Enable()

