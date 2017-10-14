"""PyDateTimePickerCtrl"""
import datetime
import wx
import wx.adv
import wx.lib.newevent
import wx.lib.masked

DatetimeChangedEvent, EVT_DATETIME_CHANGED = wx.lib.newevent.NewEvent()


class PyDateTimePickerCtrl(wx.Panel):
    """Date picker that returns python datetime object"""
    def __init__(self, parent, show_checkbox=True, **kwds):
        super(PyDateTimePickerCtrl, self).__init__(parent, **kwds)

        self.is_none = False
        self.show_checkbox = show_checkbox

        self.date_picker = wx.adv.DatePickerCtrl(self, style=wx.adv.DP_DROPDOWN)
        height = self.date_picker.GetSize().height

        self.time_spinner = wx.SpinButton(self, style=wx.SP_VERTICAL, size=(-1, height))
        self.time_picker = wx.lib.masked.TimeCtrl(self, fmt24hr=True, spinButton=self.time_spinner,
                                                  size=(-1, height), style=wx.BORDER_THEME)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.check_none = wx.CheckBox(self, size=(-1, height))
        self.check_none.SetValue(True)
        self.check_none.Bind(wx.EVT_CHECKBOX, self._on_toggle_none)
        sizer.Add(self.check_none, 0, wx.ALIGN_CENTER_VERTICAL| wx.RIGHT, border=2)
        sizer.Add(self.date_picker, 1, wx.EXPAND)
        sizer.AddSpacer(2)
        sizer.Add(self.time_picker, 1, wx.EXPAND)
        sizer.Add(self.time_spinner, 0, wx.EXPAND)
        self.SetSizer(sizer)

        if not self.show_checkbox:
            self.check_none.Hide()

        self.time_spinner.Bind(wx.EVT_SPIN, self._on_changed_datetime)
        self.time_picker.Bind(wx.EVT_TEXT, self._on_changed_datetime)
        self.date_picker.Bind(wx.adv.EVT_DATE_CHANGED, self._on_changed_datetime)

        self.check_none.SetCanFocus(True)
        self.time_picker.SetCanFocus(True)
        self.date_picker.SetCanFocus(True)

        self.set_pydatetime(None)


    def _on_changed_datetime(self, event):
        new_event = DatetimeChangedEvent()
        wx.PostEvent(self, new_event)
        event.Skip()


    def _clear(self):
        self.is_none = True
        self.check_none.SetValue(False)
        self.date_picker.Hide()
        self.time_picker.Hide()
        self.time_spinner.Hide()
        self.Layout()


    def _unclear(self):
        self.is_none = False
        self.check_none.SetValue(True)
        self.date_picker.Show()
        self.time_picker.Show()
        self.time_spinner.Show()
        self.Layout()


    def Disable(self):
        self.date_picker.Disable()
        self.time_picker.Disable()
        self.time_spinner.Disable()
        if self.show_checkbox:
            self.check_none.Hide()
            self.Layout()


    def Enable(self):
        self.date_picker.Enable()
        self.time_picker.Enable()
        self.time_spinner.Enable()
        if self.show_checkbox:
            self.check_none.Show()
            self.Layout()


    def _on_toggle_none(self, event):
        if self.check_none.GetValue():
            self.set_pydatetime(datetime.datetime.now())
            self.date_picker.SetFocus()
            self._on_changed_datetime(event)
        else:
            self._clear()


    def get_pydatetime(self):
        """Returns value as python datetime object"""
        if self.is_none:
            return None

        wxdate = self.date_picker.GetValue()
        if not wxdate.IsValid():
            return None

        time_str = self.time_picker.GetValue()

        new_time = datetime.datetime.strptime(time_str, "%H:%M:%S")

        new_datetime = datetime.datetime(
            wxdate.GetYear(),
            wxdate.GetMonth() + 1,
            wxdate.GetDay(),
            new_time.hour,
            new_time.minute,
            new_time.second
        )

        return new_datetime


    def set_pydatetime(self, pydatetime_object):
        """Sets datetime to python datetime object"""
        if pydatetime_object is None:
            self._clear()
            return
        self._unclear()

        wxdatetime = wx.DateTime()
        wxdatetime.Set(
            pydatetime_object.day,
            pydatetime_object.month - 1,
            pydatetime_object.year
        )
        self.date_picker.SetValue(wxdatetime)

        time_str = datetime.datetime.strftime(pydatetime_object, "%H:%M:%S")
        self.time_picker.ChangeValue(time_str)


def main():
    frame = wx.Frame(None)
    picker = PyDateTimePickerCtrl(None)


if __name__ == "__main__":
    app = wx.App(False)

    f = wx.Frame(None, title="Haha")

    picker = PyDateTimePickerCtrl(f, show_checkbox=False)

    #picker.set_pydatetime(None)

    def get_time(event):
        print picker.set_pydatetime(datetime.datetime.now())

    btn = wx.Button(f, label="Get Time")
    btn.Bind(wx.EVT_BUTTON, get_time)

    sizer = wx.BoxSizer(wx.VERTICAL)
    sizer.Add(picker, 0, wx.EXPAND)
    sizer.Add(btn, 0, wx.EXPAND)
    f.SetSizer(sizer)
    f.Show()

    app.MainLoop()