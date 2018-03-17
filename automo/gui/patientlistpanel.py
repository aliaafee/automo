"""Patients list panel"""
import wx

from .wardpanel import WardPanel
from .patientsearchpanel import PatientSearchPanel


class PatientListPanel(wx.Panel):
    """Patients list panel"""
    def __init__(self, parent, session, **kwds):
        super(PatientListPanel, self).__init__(parent, **kwds)

        self.session = session

        self.notebook = wx.Notebook(self)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._on_change_notebook)

        self.ward_panel = WardPanel(self.notebook, self.session)
        self.notebook.AddPage(self.ward_panel, "Ward")

        self.search_panel = PatientSearchPanel(self.notebook, self.session)
        self.notebook.AddPage(self.search_panel, "Search")

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.notebook, 1 , wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(self.sizer)


    def _patient_list_decorator(self, item, query_str):
        return item.name


    def _on_change_notebook(self, event):
        active_page_text = self.notebook.GetPageText(self.notebook.GetSelection())
        if active_page_text == "Search":
            self.search_panel.patients_list.SetSelection(-1)
        else:
            self.ward_panel.refresh()
            self.ward_panel.beds_list.SetSelection(-1)
        event.Skip()


    def refresh(self):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        active_page.refresh()


    def refresh_selected(self):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        active_page.refresh_selected()


    def refresh_all(self):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        active_page.refresh_all()
