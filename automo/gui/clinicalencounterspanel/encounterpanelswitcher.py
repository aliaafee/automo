"""Encounter panel, displays the appropriate encounter window"""
import wx

from .admissionpanel import AdmissionPanel
from .admissioncircumcision import AdmissionCircumcisionPanel

PANELS = {
    'admission' : AdmissionPanel,
    'circumcisionadmission' : AdmissionCircumcisionPanel
}


class EncounterPanelSwitcher(wx.Panel):
    """Encounter panel, displays the appropriate encounter window"""
    def __init__(self, parent, session, **kwds):
        super(EncounterPanelSwitcher, self).__init__(parent, **kwds)

        self.session = session

        self.active_panel = None
        self.panels = {}

        self._prev_active_panel = None

        self.sizer = wx.BoxSizer()
        self.SetSizer(self.sizer)


    def show_encounter_panel(self, encounter):
        if encounter is None:
            if self.active_panel is not None:
                self.active_panel.Hide()
                self.Layout()
            return

        if not self.panels.has_key(encounter.type):
            if not PANELS.has_key(encounter.type):
                if self.active_panel is not None:
                    self.active_panel.Hide()
                    self.Layout()
                return
            panel = PANELS[encounter.type]
            self.panels[encounter.type] = panel(self, self.session)
            self.sizer.Add(self.panels[encounter.type], 1, wx.EXPAND)

        self.active_panel = self.panels[encounter.type]

        for name, panel in self.panels.items():
            if panel == self.active_panel:
                panel.Show()
            else:
                panel.Hide()

        if self.active_panel != self._prev_active_panel:
            self.Layout()
            self._prev_active_panel = self.active_panel
        
        return self.active_panel
