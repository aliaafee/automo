from .enumfield import EnumField


class RelationField(EnumField):
    def __init__(self, label, str_attr, db_choices_query, value_formatter=None, required=False, editable=True, help_text=None):
        super(RelationField, self).__init__(label, str_attr, [], required, editable, help_text)
        self.db_choices_query = db_choices_query
        self.value_formatter = value_formatter
        if value_formatter is None:
            self.value_formatter = self._value_formatter
        self.choices = []

    def _value_formatter(self, value):
        return unicode(value)

    def _update_choices(self, value_search=None):
        self.choices = self.db_choices_query.all()
        choices_str = []
        selection = -1
        for index, choice in enumerate(self.choices):
            choices_str.append(self.value_formatter(choice))
            if choice == value_search:
                selection = index
        self.editor.SetItems(choices_str)
        self.editor.SetSelection(selection)

    def create_editor(self, parent):
        editor = super(RelationField, self).create_editor(parent)
        self._update_choices()
        return editor

    def set_editor_value(self, value):
        self._update_choices(value)

    def get_editor_value(self):
        selection = self.editor.GetSelection()
        if selection == -1:
            return None
        return self.choices[selection]
