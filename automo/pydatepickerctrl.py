"""PyDatePickerCtrl"""
import datetime
import wx


class PyDatePickerCtrl(wx.DatePickerCtrl):
    """Date picker that returns python datetime object"""
    def __init__(self, parent, **kwds):
        super(PyDatePickerCtrl, self).__init__(parent, **kwds)


    def get_pydatetime(self):
        """Returns value as python datetime object"""
        wxdate = self.GetValue()
        if wxdate.IsOk():
            new_date = datetime.date(
                wxdate.GetYear(),
                wxdate.GetMonth() + 1,
                wxdate.GetDay()
            )
            return new_date
        return None


    def set_pydatetime(self, pydatetime_object):
        """Sets datetime to python datetime object"""
        wxdatetime = wx.DateTime()
        wxdatetime.Set(
            pydatetime_object.day,
            pydatetime_object.month - 1,
            pydatetime_object.year
        )
        self.SetValue(wxdatetime)
