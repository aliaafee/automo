import wx

from ... import database as db
from .. import events
from .field import Field
from .formpanel import FormPanel
from .stringfield import StringField


class AddressField(Field):
    def __init__(self, label, str_attr, required=False, editable=True):
        super(AddressField, self).__init__(label, str_attr, required, editable)
        self.current_object = None

        self.fields = [
            StringField("Line 1", "line_1", editable=editable),
            StringField("Line 2", "line_2", editable=editable),
            StringField("Line 3", "line_3", editable=editable),
            StringField("City", "city", editable=editable),
            StringField("Region", "region", editable=editable),
            StringField("Country", "country", editable=editable)
        ]

    def create_editor(self, parent):
        self.editor = FormPanel(parent, db.Address, self.fields, scrollable=False, style=wx.BORDER_THEME)
        if self.editable:
            self.editor.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX))
        self.editor.Bind(events.EVT_AM_DB_FORM_CHANGED, self.on_editor_changed)
        return self.editor

    def lock_editor(self):
        self.editor.lock()

    def unlock_editor(self):
        self.editor.unlock()

    def set_editor_value(self, value):
        self.editor.set_object(value)
        self.current_object = value

    def get_editor_value(self):
        if self.current_object is None:
            self.current_object = self.editor.get_object()
        else:
            self.editor.update_object(self.current_object)
        return self.current_object
