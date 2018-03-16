"""Form to edit fields of encounter"""
import wx

from . import images
from . import events
from .encounternotebookpage import EncounterNotebookPage
from .dbform import FormPanel


class EncounterNotebookForm(EncounterNotebookPage):
    """Form to edit fields of encounter"""
    def __init__(self, parent, session, db_encounter_class, fields, scrollable=True, **kwds):
        super(EncounterNotebookForm, self).__init__(parent, session, **kwds)

        self.db_encounter_class = db_encounter_class
        self.fields = fields

        self.changed = False

        self.toolbar.AddTool(wx.ID_SAVE, "Save", images.get("save"), wx.NullBitmap, wx.ITEM_NORMAL, "Save changes", "")
        self.toolbar.Realize()

        self.toolbar.Bind(wx.EVT_TOOL, self._on_save, id=wx.ID_SAVE)

        self.form = FormPanel(self, self.db_encounter_class,
                                self.fields, scrollable=scrollable)
        self.form.Bind(events.EVT_AM_DB_FORM_CHANGED, self._on_field_changed)

        self.sizer.Add(self.form, 1, wx.EXPAND | wx.ALL, border=5)


    def _on_field_changed(self, event):
        self.changed = True
        self._update_toolbar()


    def _on_save(self, event):
        self.save_changes()


    def _update_toolbar(self):
        if self.changed:
            self.toolbar.EnableTool(wx.ID_SAVE, True)
        else:
            self.toolbar.EnableTool(wx.ID_SAVE, False)


    def is_unsaved(self):
        if self.encounter is not None:
            if self.changed:
                return True
        return False


    def save_changes(self):
        if self.encounter is not None:
            self.form.update_object(self.encounter)
            self.session.commit()
            self.changed = False
            self._update_toolbar()


    def editable_on(self):
        super(EncounterNotebookForm, self).editable_on()
        self.form.unlock()


    def editable_off(self):
        super(EncounterNotebookForm, self).editable_off()
        self.form.lock()


    def set_encounter(self, encounter):
        super(EncounterNotebookForm, self).set_encounter(encounter)

        self.form.set_object(self.encounter)

        self.changed = False
        self._update_toolbar()