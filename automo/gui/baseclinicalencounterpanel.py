"""Base Panel for Clinical Encounters"""
import wx

from .. import database as db
from . import events
from . import images
from .dbdatepicker import DbDatePicker
from .dbrelationcombo import DbRelationCombo


class BaseClinicalEncounterPanel(wx.Panel):
    """Base Panel for Clinical Encounters"""
    def __init__(self, parent, session, **kwds):
        super(BaseClinicalEncounterPanel, self).__init__(parent, **kwds)

        self.session = session
        self.encounter = None

        self.editable = True

        big_font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        self.info_panel = wx.Panel(self, style=wx.BORDER_THEME)
        self.label_title = wx.StaticText(self.info_panel, label="")
        self.label_title.SetFont(big_font)

        self.toolbar = wx.ToolBar(self.info_panel, style=wx.TB_FLAT | wx.TB_NODIVIDER)
        self.toolbar.AddStretchableSpace()
        self.create_toolbar()
        self.toolbar.Realize()

        self.txt_start_time = DbDatePicker(self.info_panel, self.session)
        self.txt_start_time.Bind(events.EVT_AM_DB_CTRL_CHANGED, self._on_change_encounter)

        self.txt_end_time = DbDatePicker(self.info_panel, self.session)
        self.txt_end_time.Bind(events.EVT_AM_DB_CTRL_CHANGED, self._on_change_encounter)

        self.label_to = wx.StaticText(self.info_panel)

        self.txt_doctor = DbRelationCombo(self.info_panel, self.session)

        time_sizer = wx.FlexGridSizer(2, 4, 2, 2)
        time_sizer.AddMany([
            (wx.StaticText(self.info_panel, label="From"), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.txt_start_time, 0, wx.EXPAND),
            (wx.StaticText(self.info_panel, label="Doctor"), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.txt_doctor, 0, wx.EXPAND),
            (self.label_to, 0, wx.ALIGN_CENTER_VERTICAL),
            (self.txt_end_time, 0, wx.EXPAND)
        ])
        time_sizer.AddSpacer(22)
        self.info_panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.label_title, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hsizer.Add(time_sizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hsizer.Add(self.info_panel_sizer, 0, wx.EXPAND)
        hsizer.Add(self.toolbar, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        self.info_panel.SetSizer(hsizer)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.info_panel, 0, wx.EXPAND | wx.BOTTOM, border=5)
        self.SetSizer(self.sizer)


    def create_toolbar(self):
        self.img_locked = images.get("locked_24")
        self.img_unlocked = images.get("unlocked_24")

        self.toolbar.AddLabelTool(wx.ID_EDIT, "Lock", self.img_unlocked, wx.NullBitmap, wx.ITEM_NORMAL, "Lock / Unlock Editing", "")
        
        self.toolbar.Bind(wx.EVT_TOOL, self._on_toggle_edit, id=wx.ID_EDIT)


    def _on_toggle_edit(self, event):
        self.set_editable(not self.editable)


    def _on_change_encounter(self, event):
        new_event = events.EncounterChangedEvent(events.ID_ENCOUNTER_CHANGED, object=self.encounter)
        wx.PostEvent(self, new_event)


    def set_title(self, title):
        self.label_title.SetLabelText(title)


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing"""
        return False


    def save_changes(self):
        """Save changes"""
        pass


    def set_editable(self, editable):
        """Set control to editable or not"""
        self.editable = editable
        if self.editable:
            self.txt_start_time.Enable()
            self.txt_end_time.Enable()
            self.txt_doctor.Enable()
            self.toolbar.SetToolNormalBitmap(wx.ID_EDIT, self.img_unlocked)
        else:
            self.txt_start_time.Disable()
            self.txt_end_time.Disable()
            self.txt_doctor.Disable()
            self.toolbar.SetToolNormalBitmap(wx.ID_EDIT, self.img_locked)


    def set(self, encounter):
        """Set The encounter"""
        self.encounter = encounter

        if self.encounter is None:
            self.unset()
            return

        self.info_panel.Show()
        self.txt_start_time.set_dbobject_attr(encounter, "start_time")
        self.txt_end_time.set_dbobject_attr(encounter, "end_time")
        self.txt_doctor.set_dbobject_attr(encounter,
                                          "personnel_id",
                                          "personnel",
                                          self.session.query(db.Doctor),
                                          "id")
        if self.encounter.is_active():
            self.set_editable(True)
            self.txt_end_time.Hide()
            self.label_to.SetLabel(" ")
        else:
            self.set_editable(False)
            self.txt_end_time.Show()
            self.label_to.SetLabel("To")

        self.label_to.SetSize(self.txt_start_time.GetSizeTuple())
        self.Layout()


    def unset(self):
        """Clear the panel"""
        self.encounter = None

        self.info_panel.Hide()
        self.txt_start_time.set_dbobject_attr(None, "")
        self.txt_end_time.set_dbobject_attr(None, "")
        self.txt_doctor.set_dbobject_attr(None, "", "", None, "")
