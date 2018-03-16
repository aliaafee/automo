from .field import Field


class FloatField(Field):
    def __init__(self, label, str_attr, required=False, editable=True):
        super(FloatField, self).__init__(label, str_attr, required, editable)

    def set_editor_value(self, value):
        self.editor.SetValue(unicode(value))

    def get_editor_value(self):
        value_str = self.editor.GetValue()
        if value_str == "":
            return None
        try:
            return float(value_str)
        except ValueError:
            return None
