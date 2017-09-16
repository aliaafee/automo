"""Patients list panel"""
import wx

from . import events
from .wardpanel import WardPanel
from .patientsearchpanel import PatientSearchPanel


class PatientListPanel(wx.Panel):
    """Patients list panel"""
    def __init__(self, parent, session, **kwds):
        super(PatientListPanel, self).__init__(parent, **kwds)

        self.session = session

        #self.patient_panel = None

        #self.toolbar = self._get_toolbar()

        self.notebook = wx.Notebook(self)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_change_notebook)

        self.ward_panel = WardPanel(self.notebook, self.session)
        #self.ward_panel.Bind(events.EVT_AM_PATIENT_SELECTED, self._on_patient_selected)
        self.notebook.AddPage(self.ward_panel, "Ward")

        self.search_panel = PatientSearchPanel(self.notebook, self.session)
        #self.search_panel.Bind(events.EVT_AM_PATIENT_SELECTED, self._on_patient_selected)
        self.notebook.AddPage(self.search_panel, "Search")

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        #self.sizer.Add(self.toolbar, 0, wx.EXPAND | wx.TOP | wx.LEFT, border=5)
        self.sizer.Add(self.notebook, 1 , wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(self.sizer)


    #def _get_toolbar(self):
    #    toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)

        #toolbar.AddLabelTool(wx.ID_REFRESH, "Refresh", images.get("refresh_24"),
        #                          wx.NullBitmap, wx.ITEM_NORMAL, "Refresh", "")

        #toolbar.AddSeparator()

    #    toolbar.AddLabelTool(wx.ID_PRINT, "Print", images.get("print_24"),
    #                              wx.NullBitmap, wx.ITEM_NORMAL, "Print", "")

        #toolbar.Bind(wx.EVT_TOOL, self._on_refresh, id=wx.ID_REFRESH)

    #    toolbar.Realize()

    #    return toolbar


    def _patient_list_decorator(self, item, query_str):
        return item.name


    def _on_change_notebook(self, event):
        active_page_text = self.notebook.GetPageText(self.notebook.GetSelection())
        if active_page_text == "Search":
            self.search_panel.patients_list.SetSelection(-1)
        else:
            self.ward_panel.beds_list.SetSelection(-1)
        event.Skip()


    def refresh(self):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        active_page.refresh()


    def refresh_selected(self):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        active_page.refresh_selected()


    #def _on_patient_selected(self, event):
    #    event = events.PatientSelectedEvent(object=event.object)
    #    wx.PostEvent(self, event)
