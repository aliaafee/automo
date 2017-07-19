"""DbRelationCtrl"""

import wx


class DbRelationCtrl(wx.TextCtrl):
    """Text ctrl that displays relation attributes. This is readonly"""
    def __init__(self, parent, session, value_formatter=None, on_change_callback=None, **kwds):
        super(DbRelationCtrl, self).__init__(parent, **kwds)

        self.session = session
        self.value_formatter = value_formatter

        #self.on_change_callback = on_change_callback

        self.db_object = None
        self.db_str_attr_id = None
        self.db_str_attr = None

        if self.value_formatter is None:
            self.value_formatter = self._value_formatter

        self.SetEditable(False)

        #self.Bind(wx.EVT_TEXT, self._on_change)


    def _value_formatter(self, rel_object):
        return unicode(rel_object)


    def set_dbobject_attr(self, db_object, str_attr_id, str_attr):
        """Set which object needs to be updated"""
        self.db_object = db_object
        self.db_str_attr_id = str_attr_id
        self.db_str_attr = str_attr

        if self.db_object is None\
                or self.db_str_attr_id == ""\
                or self.db_str_attr == "":
            self.ChangeValue("")
            return

        rel_object = getattr(self.db_object, self.db_str_attr)

        if rel_object is None:
            self.ChangeValue("")
            return

        self.ChangeValue(self.value_formatter(rel_object))


    def _on_change(self, event):
        """Updates and commits changes. Does not do anything"""
        pass
