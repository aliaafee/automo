"""
DbTextCtrl
"""
import wx


class DbTextCtrl(wx.TextCtrl):
    """
    Text ctrl that automatically updates database entry, on text change
    """
    def __init__(self, parent, session, on_change_callback=None, **kwds):
        super(DbTextCtrl, self).__init__(parent, **kwds)

        self.session = session

        self.on_change_callback = on_change_callback

        self.db_object = None
        self.db_str_attr = None

        self.Bind(wx.EVT_TEXT, self._on_change)


    def set_dbobject_attr(self, db_object, str_attr):
        """Set which object needs to be updated"""
        self.db_object = db_object
        self.db_str_attr = str_attr

        if self.db_object is None or self.db_str_attr == "":
            self.ChangeValue("")
        else:
            value = getattr(self.db_object, self.db_str_attr)
            if value is None:
                value = ""

            self.ChangeValue(value)


    def _on_change(self, event):
        """Updates and commits changes"""
        if self.db_object is None or self.db_str_attr == "":
            return

        setattr(self.db_object, self.db_str_attr, self.GetValue())

        self.session.commit()

        if self.on_change_callback is not None:
            self.on_change_callback(event)
