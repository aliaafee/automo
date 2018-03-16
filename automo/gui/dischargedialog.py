"""Discharge Dialog"""
import datetime
import wx

from .basedialog import BaseDialog
from .widgets import PyDateTimePickerCtrl


class DischargeDialog(BaseDialog):
    """Discharge Dialog"""
    def __init__(self, parent, title="Discharge", size=(500, 150), **kwds):
        super(DischargeDialog, self).__init__(parent, title=title, size=size, **kwds)

        self.set_ok_label("Discharge")

        self.txt_discharge_time = PyDateTimePickerCtrl(self)
        self.txt_discharge_time.set_pydatetime(datetime.datetime.now())

        grid_sizer = wx.FlexGridSizer(2, 2, 5, 5)
        grid_sizer.AddMany([
            (wx.StaticText(self, label="Discharge Date"), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.txt_discharge_time, 0, wx.EXPAND)
        ])
        grid_sizer.AddGrowableCol(1)
        grid_sizer.AddGrowableRow(1)

        self.add_to_sizer(grid_sizer, 1, wx.EXPAND)


    def get_discharge_time(self):
        return self.txt_discharge_time.get_pydatetime()
