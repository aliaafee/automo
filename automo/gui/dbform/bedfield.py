import wx

from ..dbcombobox import DbComboBox
from .field import Field


class BedField(Field):
    def __init__(self, label, str_attr, wards_list, required=False, editable=True, help_text=None):
        super(BedField, self).__init__(label, str_attr, required, editable, help_text)
        self.wards_list = wards_list

    def create_editor(self, parent):
        self.editor = wx.Panel(parent)

        self.cmb_ward = DbComboBox(self.editor)
        self.cmb_ward.Bind(wx.EVT_COMBOBOX, self._on_change_ward)
        self.cmb_ward.set_items(
            self.wards_list
        )

        self.cmb_bed = DbComboBox(self.editor)
        self.cmb_bed.Bind(wx.EVT_COMBOBOX, self.on_editor_changed)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.cmb_ward, 1 , wx.EXPAND)
        sizer.Add(self.cmb_bed, 1, wx.EXPAND)

        self.editor.SetSizer(sizer)

        return self.editor

    def _update_cmb_bed(self):
        selected_ward = self.cmb_ward.get_selected_item()
        
        if selected_ward is None:
            self.cmb_bed.clear()
        else:
            self.cmb_bed.set_items(selected_ward.beds)

        self.cmb_bed.SetSelection(-1)

    def _on_change_ward(self, event):
        self._update_cmb_bed()
        self.on_editor_changed(event)

    def _bed_decorator(self, bed):
        html = '<font size="2">'\
                    '<table width="100%">'\
                        '<tr>'\
                            '<td valign="top">{0}</td>'\
                        '</tr>'\
                    '</table>'\
                '</font>'
        return html.format(str(bed))

    def lock_editor(self):
        self.cmb_ward.Disable()
        self.cmb_bed.Disable()

    def unlock_editor(self):
        self.cmb_ward.Enable()
        self.cmb_bed.Enable()

    def set_editor_value(self, value):
        if value is None:
            self.cmb_bed.SetSelection(-1)
            return

        self.cmb_ward.set_selected_item(value.ward)
        self._update_cmb_bed()
        self.cmb_bed.set_selected_item(value)

    def get_editor_value(self):
        return self.cmb_bed.get_selected_item()
