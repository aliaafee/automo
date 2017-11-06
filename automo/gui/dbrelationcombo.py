"""DbRelationCombo"""
import wx

from .events import DbCtrlChangedEvent


class DbRelationCombo(wx.ComboBox):
    """Combo ctrl that displays relation attributes. Choices obtained from query"""
    def __init__(self, parent, session, value_formatter=None, on_change_callback=None, **kwds):
        super(DbRelationCombo, self).__init__(parent, style=wx.CB_READONLY, **kwds)

        self.session = session
        self.value_formatter = value_formatter

        self.on_change_callback = on_change_callback

        self.db_object = None
        self.db_str_attr_id = None
        self.db_str_attr = None
        self.db_choices_query = None
        self.db_choices_id_str = None

        self.choices = []
        self.Append("<None>")
        self.SetSelection(0)

        if self.value_formatter is None:
            self.value_formatter = self._value_formatter

        self.Bind(wx.EVT_COMBOBOX, self._on_change)


    def _value_formatter(self, rel_object):
        return unicode(rel_object)


    def get_selected_object(self):
        """Returns the selected database object"""
        index = self.GetSelection() - 1
        if index == -1:
            return None
        try:
            return self.choices[index]
        except IndexError:
            return None


    def set_dbobject_attr(self, db_object, str_attr_id, str_attr,
                          db_choices_query, db_choices_id_str):
        """Set which object needs to be updated"""
        self.db_object = db_object
        self.db_str_attr_id = str_attr_id
        self.db_str_attr = str_attr
        self.db_choices_query = db_choices_query
        self.db_choices_id_str = db_choices_id_str

        if self.db_object is None\
                or self.db_str_attr_id == ""\
                or self.db_str_attr == "":
            self.Clear()
            return

        rel_object = getattr(self.db_object, self.db_str_attr)

        self.Clear()
        self.Append("<None>")
        self.choices = self.db_choices_query.all()
        selection_index = 0
        list_index = 1
        for choice in self.choices:
            if rel_object is not None:
                if rel_object == choice:
                    selection_index = list_index
            choice_str = self.value_formatter(choice)
            self.Append(choice_str, choice)
            list_index += 1

        self.SetSelection(selection_index)


    def _on_change(self, event):
        """Updates and commits changes. Does not do anything"""
        selected_object = self.get_selected_object()

        if selected_object is None:
            new_value = None
        else:
            new_value = getattr(selected_object, self.db_choices_id_str)

        setattr(self.db_object, self.db_str_attr_id, new_value)

        self.session.commit()

        event = DbCtrlChangedEvent(object=self.db_object)
        wx.PostEvent(self, event)

