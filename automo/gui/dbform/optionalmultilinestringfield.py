import wx

from .field import Field


class OptionalMultilineStringField(Field):
    def __init__(self, label, str_attr, lines=3, required=False, editable=True):
        super(OptionalMultilineStringField, self).__init__(label, str_attr, required, editable)
        self.lines = lines

    def _on_check(self, event):
        if self.checkbox.GetValue() is True:
            self.textbox.Show()
        else:
            self.textbox.Hide()
        self.parent.Layout()
        self.on_editor_changed(event)

    def create_editor(self, parent):
        self.parent = parent
        
        self.editor = wx.Panel(parent)
        self.checkbox = wx.CheckBox(self.editor)
        self.textbox = wx.TextCtrl(self.editor, style=wx.TE_MULTILINE, size=(-1, self.lines * 15))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.checkbox, 0, wx.RIGHT | wx.ALIGN_TOP, border=2),
        sizer.Add(self.textbox, 1, wx.EXPAND)
        self.editor.SetSizer(sizer)

        self.textbox.Hide()

        if not self.editable:
            self.lock_editor()
        else:
            self.checkbox.Bind(wx.EVT_CHECKBOX, self._on_check)
            self.textbox.Bind(wx.EVT_TEXT, self.on_editor_changed)

        return self.editor

    def lock_editor(self):
        self.checkbox.Disable()
        self.textbox.Disable()

    def unlock_editor(self):
        self.checkbox.Enable()
        self.textbox.Enable()

    def set_editor_value(self, value):
        if value is None:
            self.textbox.ChangeValue("")
            self.textbox.Hide()
            self.checkbox.SetValue(False)
            return
        self.textbox.ChangeValue(value)
        self.textbox.Show()
        self.checkbox.SetValue(True)

    def get_editor_value(self):
        if self.checkbox.GetValue() is False:
            return None
        str_value = self.textbox.GetValue()
        if str_value == "":
            return None
        return str_value
