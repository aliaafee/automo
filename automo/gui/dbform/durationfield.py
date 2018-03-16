from ... import config
from .field import Field


class DurationField(Field):
    def __init__(self, label, str_attr, required=False, editable=True):
        super(DurationField, self).__init__(label, str_attr, required, editable)

    def set_editor_value(self, value):
        duration_str = config.format_duration(value)
        self.editor.SetValue(duration_str)

    def get_editor_value(self):
        duration_str = self.editor.GetValue()
        if duration_str == "":
            return None

        try:
            return config.parse_duration(duration_str)
        except ValueError:
            return None

    def is_valid(self):
        duration_str = self.editor.GetValue()
        if duration_str == "" and self.required:
            return False, "cannot be blank"

        try:
            duration =  config.parse_duration(duration_str)
        except ValueError:
            return False, "invalid duration format use __y __m __d"

        return True, ""
