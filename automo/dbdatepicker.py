"""
DbDatePicker
"""
import datetime
import wx


class DbDatePicker(wx.DatePickerCtrl):
    """
    Date picker ctrl that automatically updates database entry, on text change
    """
    def __init__(self, parent, session, on_change_callback=None,
                 style=wx.DP_DROPDOWN, **kwds):
        super(DbDatePicker, self).__init__(parent, style=style, **kwds)

        self.session = session

        self.on_change_callback = on_change_callback

        self.db_object = None
        self.db_str_attr = None

        self.Bind(wx.EVT_DATE_CHANGED, self._on_change)


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

        wxdatetime = wx.DateTime()
        wxdatetime.Set(
            value.day,
            value.month - 1,
            value.year
        )
        self.SetValue(wxdatetime)
        self.Show()


    def _on_change(self, event):
        """Updates and commits changes"""
        if self.db_object is None or self.db_str_attr == "":
            return

        wxdate = self.GetValue()
        new_date = datetime.date(
            wxdate.GetYear(),
            wxdate.GetMonth() + 1,
            wxdate.GetDay()
        )

        setattr(self.db_object, self.db_str_attr, new_date)

        self.session.commit()

        if self.on_change_callback is not None:
            self.on_change_callback(event)
