import wx

from .field import Field


class MultilineStringField(Field):
    def __init__(self, label, str_attr, lines=3, required=False, editable=True):
        super(MultilineStringField, self).__init__(label, str_attr, required, editable)
        self.lines = lines

    def create_editor(self, parent):
        self.editor = wx.TextCtrl(parent, style=wx.TE_MULTILINE, size=(-1, self.lines * 15))
        if not self.editable:
            self.editor.SetEditable(False)
        else:
            self.editor.Bind(wx.EVT_TEXT, self.on_editor_changed)
        return self.editor
