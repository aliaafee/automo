"""PyDatePickerCtrl"""
import datetime
import wx
import wx.adv
import wx.lib.newevent
import wx.lib.masked

DatetimeChangedEvent, EVT_DATETIME_CHANGED = wx.lib.newevent.NewEvent()


class PyDatePickerCtrl(wx.Panel):
    """Date picker that returns python datetime object.
      Does not clobber the time component of a datetime object. Only changes
      The date component."""
    def __init__(self, parent, show_checkbox=True, **kwds):
        super(PyDatePickerCtrl, self).__init__(parent, **kwds)

        self.pydatetime_object = None

        self.is_none = True
        self.show_checkbox = show_checkbox

        self.date_picker = wx.adv.DatePickerCtrl(self, style=wx.adv.DP_DROPDOWN)
        height = self.date_picker.GetSize().height

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.check_none = wx.CheckBox(self, size=(-1, height))
        self.check_none.SetValue(True)
        self.check_none.Bind(wx.EVT_CHECKBOX, self._on_toggle_none)
        sizer.Add(self.check_none, 0, wx.ALIGN_CENTER_VERTICAL| wx.RIGHT, border=2)
        sizer.Add(self.date_picker, 1, wx.EXPAND)
        self.SetSizer(sizer)

        if not self.show_checkbox:
            self.check_none.Hide()

        self.date_picker.Bind(wx.adv.EVT_DATE_CHANGED, self._on_changed)

        self.check_none.SetCanFocus(True)
        self.date_picker.SetCanFocus(True)

        self.check_none.SetValue(False)
        self.date_picker.Hide()


    def _on_changed(self, event):
        new_event = DatetimeChangedEvent()
        wx.PostEvent(self, new_event)
        event.Skip()


    def _clear(self):
        self.is_none = True
        self.check_none.SetValue(False)
        self.date_picker.Hide()
        self.Layout()


    def _unclear(self):
        self.is_none = False
        self.check_none.SetValue(True)
        self.date_picker.Show()
        self.Layout()


    def Disable(self):
        self.date_picker.Disable()
        if self.show_checkbox:
            self.check_none.Hide()
        self.Layout()


    def Enable(self):
        self.date_picker.Enable()
        if self.show_checkbox:
            self.check_none.Show()
        self.Layout()


    def set_to_now(self):
        today = datetime.date.today()
        self.set_pydatetime(datetime.datetime(
            today.year,
            today.month,
            today.day
        ))


    def _on_toggle_none(self, event):
        if self.check_none.GetValue():
            if self.pydatetime_object is None:
                self.set_to_now()
            self.set_pydatetime(self.pydatetime_object)
            self.date_picker.SetFocus()
        else:
            self._clear()
        self._on_changed(event)


    def _get_pydate(self):
        if self.is_none:
            return None

        wxdate = self.date_picker.GetValue()
        if not wxdate.IsValid():
            return None

        return datetime.date(
            wxdate.GetYear(),
            wxdate.GetMonth() + 1,
            wxdate.GetDay()
        )


    def get_pydatetime(self):
        """Returns value as python datetime object"""
        new_date = self._get_pydate()

        if new_date is None:
            return None

        if self.pydatetime_object is None:
            self.pydatetime_object = datetime.datetime.combine(
                new_date,
                datetime.time(0, 0, 0)
            )
            return self.pydatetime_object


        self.pydatetime_object = datetime.datetime.combine(
            new_date,
            datetime.time(
                self.pydatetime_object.hour,
                self.pydatetime_object.minute,
                self.pydatetime_object.second
            )
        )
        return self.pydatetime_object


    def _set_pydate(self, pydate_object):
        if pydate_object is None:
            return

        wxdatetime = wx.DateTime()
        wxdatetime.Set(
            pydate_object.day,
            pydate_object.month - 1,
            pydate_object.year
        )
        self.date_picker.SetValue(wxdatetime)
        

    def set_pydatetime(self, pydatetime_object):
        """Sets datetime to python datetime object"""
        self.pydatetime_object = pydatetime_object

        if self.pydatetime_object is None:
            self._clear()
            return

        self._unclear()
        self._set_pydate(self.pydatetime_object)




if __name__ == "__main__":
    app = wx.App(False)

    f = wx.Frame(None, title="Haha")

    def set_time(event):
        picker.set_pydatetime(datetime.datetime.now())

    def get_time(event):
        print picker.get_pydatetime()

    def on_change(event):
        print "Date changed"

    picker = PyDatePickerCtrl(f, show_checkbox=True)
    picker.Bind(EVT_DATETIME_CHANGED, on_change)

    btn1 = wx.Button(f, label="Set Time to now")
    btn1.Bind(wx.EVT_BUTTON, set_time)

    btn2 = wx.Button(f, label="Get Time")
    btn2.Bind(wx.EVT_BUTTON, get_time)

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(picker, 0, wx.EXPAND)
    sizer.Add(btn1, 0, wx.EXPAND)
    sizer.Add(btn2, 0, wx.EXPAND)
    f.SetSizer(sizer)
    f.Show()

    app.MainLoop()
