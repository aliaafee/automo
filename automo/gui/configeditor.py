"""Configuration Editor"""
import wx

from .. import config
from . import guiconfig


class ConfigEditor(wx.Panel):
    """Configuration Editor"""
    def __init__(self, parent, **kwds):
        super(ConfigEditor, self).__init__(parent, **kwds)

        self.fields = [
            ("Startup Interface", guiconfig, 'STARTUP_INTERFACE'),
            ("Date Format", config, 'DATE_FORMAT'),
            ("Date Time Format", config, 'DATETIME_FORMAT'),
            ("Report Title", config, 'REPORT_HEAD_TITLE'),
            ("Report Subtitle 1", config, 'REPORT_HEAD_SUBTITLE1'),
            ("Report Subtitle 2", config, 'REPORT_HEAD_SUBTITLE2'),
            ("Report Logo Right", config, 'REPORT_HEAD_LOGO_RIGHT'),
            ("Report Logo Left", config, 'REPORT_HEAD_LOGO_LEFT'),
            ("Batch Import Columns", config, 'BATCH_IMPORT_COLUMNS')
        ]

        sizer = wx.FlexGridSizer(2, 2, 2)

        self.controls = []
        for label, field_class, field_attr in self.fields:
            control = wx.TextCtrl(self)
            control.ChangeValue(getattr(field_class, field_attr))
            control.Bind(wx.EVT_TEXT, self._on_change_field)
            self.controls.append(control)
            sizer.Add(wx.StaticText(self, label=label), 0 , wx.ALIGN_CENTER_VERTICAL)
            sizer.Add(control, 0, wx.EXPAND)
        
        sizer.AddGrowableCol(1)

        self.SetSizer(sizer)


    def _on_change_field(self, event):
        control = event.GetEventObject()
        try:
            field_index = self.controls.index(control)
        except ValueError:
            return
        else:
            value = control.GetValue()
            label, field_class, field_attr = self.fields[field_index]
            setattr(field_class, field_attr, value)
