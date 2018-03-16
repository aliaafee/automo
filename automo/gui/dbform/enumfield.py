import wx
from .field import Field


class EnumField(Field):
    def __init__(self, label, str_attr, choices, required=False, editable=True, help_text=None):
        super(EnumField, self).__init__(label, str_attr, required, editable, help_text)
        self.choices = choices

    def create_editor(self, parent):
        self.editor = wx.Choice(parent)
        self.editor.SetItems(self.choices)
        if not self.editable:
            self.editor.Disable()
        else:
            self.editor.Bind(wx.EVT_CHOICE, self.on_editor_changed)
        return self.editor

    def lock_editor(self):
        self.editor.Disable()

    def unlock_editor(self):
        self.editor.Enable()

    def set_editor_value(self, value):
        if value in self.choices:
            index = self.choices.index(value)
            self.editor.SetSelection(index)
        else:
            self.editor.SetSelection(-1)

    def get_editor_value(self):
        selection = self.editor.GetSelection()
        if selection != -1:
            return self.choices[selection]
        return None
