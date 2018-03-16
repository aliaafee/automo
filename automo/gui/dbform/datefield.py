from ..widgets import PyDatePickerCtrl, EVT_DATETIME_CHANGED
from .field import Field


class DateField(Field):
    def __init__(self, label, str_attr, required=False, editable=True):
        super(DateField, self).__init__(label, str_attr, required, editable)

    def create_editor(self, parent):
        self.editor = PyDatePickerCtrl(parent)
        if not self.editable:
            self.editor.Disable()
        else:
            self.editor.Bind(EVT_DATETIME_CHANGED, self.on_editor_changed)
        return self.editor

    def lock_editor(self):
        self.editor.Disable()

    def unlock_editor(self):
        self.editor.Enable()

    def set_editor_value(self, value):
        self.editor.set_pydatetime(value)

    def get_editor_value(self):
        return self.editor.get_pydatetime()
