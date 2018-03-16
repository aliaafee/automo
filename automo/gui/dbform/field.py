import wx

from .. import events
from .. import images


class Field(object):
    def __init__(self, label, str_attr, required=False, editable=True, help_text=None):
        self.label = label
        self.str_attr = str_attr
        self.editable = editable
        self.editor = None
        self.db_object = None
        self.required = required
        self.help_text = help_text

    def create_editor(self, parent):
        self.editor = wx.TextCtrl(parent)
        if not self.editable:
            self.editor.SetEditable(False)
        else:
            self.editor.Bind(wx.EVT_TEXT, self.on_editor_changed)
        return self.editor

    def lock_editor(self):
        self.editor.SetEditable(False)

    def unlock_editor(self):
        self.editor.SetEditable(True)

    #def bind_editor_onchange(self, callable_function):
    #    self.editor.Bind(wx.EVT_TEXT, callable_function)

    def on_editor_changed(self, event):
        """Editor changed"""
        changed_event = events.DbFormChangedEvent(object=self)
        wx.PostEvent(self.editor.GetParent(), changed_event)

    def create_label(self, parent):
        if self.required:
            label = "{}*".format(self.label)
        else:
            label = self.label
        return wx.StaticText(parent, label=label)

    def create_help_button(self, parent):
        if self.help_text is None:
            return None
        help_button = wx.BitmapButton(parent, bitmap=images.get('help_24'),
                                      style=wx.BU_AUTODRAW | wx.BORDER_NONE, size=wx.Size(21, 21))
        help_button.Bind(wx.EVT_BUTTON, self._on_help_button)
        return help_button

    def _on_help_button(self, event):
        wx.MessageBox(self.help_text, "Field Help")

    def set_editor_value(self, value):
        if value is None:
            self.editor.ChangeValue("")
            return
        self.editor.ChangeValue(value)

    def get_editor_value(self):
        value_str = self.editor.GetValue()
        if value_str == "":
            return None
        return value_str

    def clear(self):
        self.set_editor_value(None)

    def set_object(self, db_object):
        self.db_object = db_object
        value = getattr(self.db_object, self.str_attr)
        self.set_editor_value(value)

    def update_object(self, db_object):
        setattr(db_object, self.str_attr, self.get_value())

    def get_value(self):
        return self.get_editor_value()

    def is_valid(self):
        if self.required:
            if self.get_value() is None:
                return False, "cannot be blank"
        return True, ""
