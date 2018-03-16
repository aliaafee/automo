"""Bed Selector"""
import wx

from .. import database as db
from .widgets import DbComboBox, DbQueryResultBox
from .basedialog import BaseDialog


class BedSelectorPanel(wx.Panel):
    """Select Bed"""
    def __init__(self, parent, session, current_bed=None, empty_beds=False):
        super(BedSelectorPanel, self).__init__(parent)

        self.session = session
        self.empty_beds = empty_beds
        self.current_bed = current_bed

        self.cmb_ward = DbComboBox(self)
        self.cmb_ward.Bind(wx.EVT_COMBOBOX, self._on_change_ward)
        self.cmb_ward.set_items(
            self.session.query(db.Ward)
        )
        if current_bed is not None:
            self.cmb_ward.set_selected_item(current_bed.ward)

        self.beds_list = DbQueryResultBox(self, self._bed_decorator)

        grid_sizer = wx.FlexGridSizer(2, 2, 5, 5)

        grid_sizer.AddMany([
            (wx.StaticText(self, label="Ward     "), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.cmb_ward, 1, wx.EXPAND),
            (wx.StaticText(self, label="Bed"), 0, wx.ALIGN_TOP),
            (self.beds_list, 1, wx.EXPAND),
        ])

        grid_sizer.AddGrowableCol(1)
        grid_sizer.AddGrowableRow(1)

        self.SetSizer(grid_sizer)

        self._on_change_ward(None)

    def _bed_decorator(self, bed, query_string):
        html = '<font size="2">'\
                    '<table width="100%">'\
                        '<tr>'\
                            '<td valign="top">{0}</td>'\
                        '</tr>'\
                    '</table>'\
                '</font>'
        return html.format(str(bed))

    def _on_change_ward(self, event):
        selected_ward = self.cmb_ward.get_selected_item()

        if selected_ward is None:
            self.beds_list.clear()
        else:
            query_result = self.session.query(db.Bed)\
                                .filter(db.Bed.ward_id == selected_ward.id)
            if self.empty_beds:
                query_result = query_result.filter(db.Bed.admission == None)

            if self.current_bed is not None:
                query_result = query_result.filter(db.Bed.id != self.current_bed.id)

            self.beds_list.set_result(query_result)

    def get_bed(self):
        return self.beds_list.get_selected_object()




class BedSelectorDialog(BaseDialog):
    """Select Bed Dialog"""
    def __init__(self, parent, session, current_bed=None, empty_beds=False, size=(500, 200), title="Select Bed"):
        super(BedSelectorDialog, self).__init__(parent, size=size, title=title)

        self.bedselector = BedSelectorPanel(self, session, current_bed, empty_beds)
        self.add_to_sizer(self.bedselector, 1, wx.EXPAND)

    def get_bed(self):
        return self.bedselector.get_bed()
