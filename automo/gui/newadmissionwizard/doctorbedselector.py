"""Select Doctor and Bed"""
import wx

from ... import database as db
from ..dbcombobox import DbComboBox
from ..dbqueryresultbox import DbQueryResultBox
from .basepage import BasePage


class DoctorBedSelectorPage(BasePage):
    """Select Doctor and Bed"""
    def __init__(self, parent, session):
        super(DoctorBedSelectorPage, self).__init__(parent, session, "Select Bed")

        self.cmb_doctor = DbComboBox(self)
        self.cmb_doctor.set_items(
            self.session.query(db.Doctor)
        )

        self.cmb_ward = DbComboBox(self)
        self.cmb_ward.Bind(wx.EVT_COMBOBOX, self._on_change_ward)
        self.cmb_ward.set_items(
            self.session.query(db.Ward)
        )

        self.beds_list = DbQueryResultBox(self, self._bed_decorator)

        grid_sizer = wx.FlexGridSizer(3, 2, 5, 5)
        grid_sizer.AddMany([
            (wx.StaticText(self, label="Admitting Doctor"), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.cmb_doctor, 1, wx.EXPAND),
            (wx.StaticText(self, label="Ward"), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.cmb_ward, 1, wx.EXPAND),
            (wx.StaticText(self, label="Bed"), 0, wx.ALIGN_CENTER_VERTICAL),
        ])
        grid_sizer.AddGrowableCol(1)

        self.sizer.Add(grid_sizer, 0 , wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        self.sizer.Add(self.beds_list, 1, wx.EXPAND | wx.ALL, border=5)

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
                                .filter(db.Bed.ward_id == selected_ward.id)\
                                .filter(db.Bed.admission == None)
            self.beds_list.set_result(query_result)

    def is_valid(self):
        selected_doc = self.cmb_doctor.get_selected_item()
        if selected_doc is None:
            self.error_message = "Select Admitting Doctor"
            return False
        selected_bed = self.beds_list.get_selected_object()
        if selected_bed is None:
            self.error_message = "Select a bed"
            return False
        return True

    def get_bed(self):
        return self.beds_list.get_selected_object()

    def get_doctor(self):
        return self.cmb_doctor.get_selected_item()
