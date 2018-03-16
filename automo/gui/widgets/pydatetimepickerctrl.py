"""PyDateTimePickerCtrl"""
import datetime
import wx
import wx.adv
import wx.lib.newevent
import wx.lib.masked

from . import pydatepickerctrl
from .pydatepickerctrl import EVT_DATETIME_CHANGED

class PyDateTimePickerCtrl(pydatepickerctrl.PyDatePickerCtrl):
    """Datetime picker that returns python datetime object"""
    def __init__(self, parent, show_checkbox=True, **kwds):
        super(PyDateTimePickerCtrl, self).__init__(parent, **kwds)

        height = self.date_picker.GetSize().height

        self.time_spinner = wx.SpinButton(self, style=wx.SP_VERTICAL, size=(-1, height))
        self.time_picker = wx.lib.masked.TimeCtrl(self, fmt24hr=True, spinButton=self.time_spinner,
                                                  size=(-1, height), style=wx.BORDER_THEME)

        #self.time_spinner.Bind(wx.EVT_SPIN, self._on_changed)
        self.time_picker.Bind(wx.EVT_TEXT, self._on_changed)

        sizer = self.GetSizer()
        sizer.AddSpacer(2)
        sizer.Add(self.time_picker, 1, wx.EXPAND)
        sizer.Add(self.time_spinner, 0, wx.EXPAND)

        self.time_spinner.Hide()
        self.time_picker.Hide()


    def _clear(self):
        self.time_picker.Hide()
        self.time_spinner.Hide()
        super(PyDateTimePickerCtrl, self)._clear()


    def _unclear(self):
        self.time_picker.Show()
        self.time_spinner.Show()
        super(PyDateTimePickerCtrl, self)._unclear()


    def Disable(self):
        self.time_spinner.Disable()
        self.time_picker.Disable()
        super(PyDateTimePickerCtrl, self).Disable()


    def Enable(self):
        self.time_spinner.Enable()
        self.time_picker.Enable()
        super(PyDateTimePickerCtrl, self).Enable()


    def set_to_now(self):
        self.set_pydatetime(datetime.datetime.now())


    def _get_pytime(self):
        if self.is_none:
            return None

        time_str = self.time_picker.GetValue()
        return datetime.datetime.strptime(time_str, "%H:%M:%S").time()


    def get_pydatetime(self):
        """Returns value as python datetime object"""
        new_date = self._get_pydate()

        if new_date is None:
            return None

        new_time = self._get_pytime()

        if new_time is None:
            return None
        self.pydatetime_object = datetime.datetime.combine(
            new_date,
            new_time
        )
        return self.pydatetime_object


    def set_pydatetime(self, pydatetime_object):
        """Sets datetime to python datetime object"""
        self.pydatetime_object = pydatetime_object

        if self.pydatetime_object is None:
            self._clear()
            return

        self._unclear()
        self._set_pydate(self.pydatetime_object)

        time_str = datetime.datetime.strftime(pydatetime_object, "%H:%M:%S")
        self.time_picker.ChangeValue(time_str)




if __name__ == "__main__":
    app = wx.App(False)

    f = wx.Frame(None, title="Haha")

    def set_time(event):
        picker.set_pydatetime(datetime.datetime.now())

    def get_time(event):
        print picker.get_pydatetime()

    def on_change(event):
        print "Date changed"

    picker = PyDateTimePickerCtrl(f, show_checkbox=True)
    picker.Bind(pydatepickerctrl.EVT_DATETIME_CHANGED, on_change)

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