import wx

from .field import Field


class CheckBoxField(Field):
    def __init__(self, label, str_attr, required=False, editable=True):
        super(CheckBoxField, self).__init__(label, str_attr, required, editable)


    def create_editor(self, parent):
        self.parent = parent
        
        self.editor = wx.CheckBox(self.parent, style=wx.CHK_3STATE | wx.CHK_ALLOW_3RD_STATE_FOR_USER)

        self.editor.Bind(wx.EVT_CHECKBOX, self.on_editor_changed)
        
        return self.editor

    def lock_editor(self):
        self.editor.Disable()
        
    def unlock_editor(self):
        self.editor.Enable()

    def set_editor_value(self, value):
        if value is None:
            self.editor.Set3StateValue(wx.CHK_UNDETERMINED)
        elif value is True:
            self.editor.Set3StateValue(wx.CHK_CHECKED)
        else:
            self.editor.Set3StateValue(wx.CHK_UNCHECKED)

    def get_editor_value(self):
        editor_value = self.editor.Get3StateValue()
        if editor_value == wx.CHK_UNDETERMINED:
            return None
        elif editor_value == wx.CHK_CHECKED:
            return True
        else:
            return False
