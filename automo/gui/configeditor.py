"""Configuration Editor"""
import wx

from .configloader import CONFIG_FIELDS

EDITABLE_FIELDS = [
    'default-interface',
    'date-format',
    'datetime-format',
    'report-head-title',
    'report-head-subtitle1',
    'report-head-subtitle2',
    'report-head-subtitle3',
    'report-head-logo-right',
    'report-head-logo-left',
]


class ConfigEditor(wx.ScrolledWindow):
    """Configuration Editor"""
    def __init__(self, parent, **kwds):
        super(ConfigEditor, self).__init__(parent, style=wx.VSCROLL, **kwds)

        self.SetScrollbars(20,20,55,40)

        grid_sizer = wx.FlexGridSizer(2, 2, 2)

        self.controls = []
        for filed_name in EDITABLE_FIELDS:
            label, module, attr = CONFIG_FIELDS[filed_name]
            value = getattr(module, attr)

            control = wx.TextCtrl(self)
            control.ChangeValue(value)
            control.Bind(wx.EVT_TEXT, self._on_change_field)
            grid_sizer.Add(wx.StaticText(self, label=label), 0 , wx.ALIGN_CENTER_VERTICAL)
            grid_sizer.Add(control, 0, wx.EXPAND)

            self.controls.append(control)
            
        
        grid_sizer.AddGrowableCol(1)

        sizer = wx.BoxSizer()
        sizer.Add(grid_sizer, 1, wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(sizer)


    def _on_change_field(self, event):
        control = event.GetEventObject()
        try:
            field_index = self.controls.index(control)
        except ValueError:
            return
        else:
            value = control.GetValue()
            label, module, attr = CONFIG_FIELDS[EDITABLE_FIELDS[field_index]]
            setattr(module, attr, value)
