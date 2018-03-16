from .field import Field


class StringField(Field):
    def __init__(self, label, str_attr, required=False, editable=True):
        super(StringField, self).__init__(label, str_attr, required, editable)
