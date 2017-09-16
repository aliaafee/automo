"""Base Panel for Clinical Encounters"""
import wx

from . import events
from .dbdatepicker import DbDatePicker
from .dbrelationcombo import DbRelationCombo


class BaseClinicalEncounterPanel(wx.Panel):
    """Base Panel for Clinical Encounters"""
    def __init__(self, parent, session, **kwds):
        super(BaseClinicalEncounterPanel, self).__init__(parent, **kwds)

        self.session = session
        self.encounter = None

        self.editable = True

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)
        self.toolbar.AddStretchableSpace()
        self.toolbar.Realize()

        big_font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        self.info_panel = wx.Panel(self, style=wx.BORDER_RAISED)
        self.label_title = wx.StaticText(self.info_panel, label="")
        self.label_title.SetFont(big_font)

        self.txt_start_time = DbDatePicker(self, self.session)
        self.txt_start_time.Bind(events.EVT_AM_DB_CTRL_CHANGED, self._on_change_encounter)

        self.txt_end_time = DbDatePicker(self, self.session)
        self.txt_end_time.Bind(events.EVT_AM_DB_CTRL_CHANGED, self._on_change_encounter)

        self.txt_admitting_doctor = DbRelationCombo(self, self.session)

        time_sizer = wx.FlexGridSizer(2, 2, 2, 2)
        time_sizer.AddMany([
            (wx.StaticText(self.info_panel, label="Start Time"), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.txt_start_time, 0, wx.EXPAND),
            (wx.StaticText(self.info_panel, label="End Time"), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.txt_end_time, 0, wx.EXPAND),
        ])

