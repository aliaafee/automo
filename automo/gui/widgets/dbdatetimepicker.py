"""DbDateTimePicker"""
import datetime
import wx

from .pydatetimepickerctrl import PyDateTimePickerCtrl, EVT_DATETIME_CHANGED
from ..events import DbCtrlChangedEvent


class DbDateTimePicker(PyDateTimePickerCtrl):
    """Date picker ctrl that automatically updates database entry, on text change"""
    def __init__(self, parent, session, **kwds):
        super(DbDateTimePicker, self).__init__(parent, show_checkbox=False, **kwds)

        self.session = session

        self.db_object = None
        self.db_str_attr = None

        self.Bind(EVT_DATETIME_CHANGED, self._on_change)


    def set_dbobject_attr(self, db_object, str_attr):
        """Set which object needs to be updated"""
        self.db_object = db_object
        self.db_str_attr = str_attr

        if self.db_object is None or self.db_str_attr == "":
            self.Hide()
            return

        value = getattr(self.db_object, self.db_str_attr)
        if value is None:
            self.Hide()
            return

        self.set_pydatetime(value)

        self.Show()


    def _on_change(self, event):
        """Updates and commits changes"""
        if self.db_object is None or self.db_str_attr == "":
            return

        new_date = self.get_pydatetime()

        setattr(self.db_object, self.db_str_attr, new_date)

        self.session.commit()

        event = DbCtrlChangedEvent(object=self.db_object)
        wx.PostEvent(self, event)
