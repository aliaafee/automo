"""Editor for wards and beds"""
import wx

from ... import database as db
from .. import events
from .. import images
from ..dbform import StringField, CheckBoxField
from ..widgets import DbQueryResultGrid, GridColumnString
from ..basedialog import BaseDialog
from .listformeditor import ListFormEditor

ID_ADD_BEDS = wx.NewId()


class WardEditor(ListFormEditor):
    """Editor for wards and beds"""
    def __init__(self, parent, session, **kwds):
        fields = [
            StringField("Ward Name", 'name'),
            StringField("Bed Prefix", 'bed_prefix'),
            CheckBoxField("Active", 'active')
        ]

        super(WardEditor, self).__init__(parent, session, db.Ward, fields, **kwds)

        self.beds_grid = DbQueryResultGrid(self._left_panel, session)
        self.beds_grid.add_column(GridColumnString("Bed Number", 'number', editable=True, width=120))
        self.beds_grid.Bind(events.EVT_AM_DB_GRID_CELL_CHANGED, self._on_bed_edited)

        sizer = self._left_panel.GetSizer()
        sizer.Add(self.beds_grid, 1, wx.EXPAND | wx.ALL, border=5)
        self.beds_grid.Hide()


    def create_toolbar(self):
        super(WardEditor, self).create_toolbar()
        self.toolbar.AddSeparator()
        self.toolbar.AddTool(ID_ADD_BEDS, "Add Beds", images.get("admit"), wx.NullBitmap, wx.ITEM_NORMAL, "Add Beds", "")
        self.toolbar.Bind(wx.EVT_TOOL, self._on_add_beds, id=ID_ADD_BEDS)

    def _on_bed_edited(self, item):
        pass


    def _on_add_beds(self, event):
        if self.selected_item is None:
            return

        dlg = BaseDialog(self)
        dlg.set_ok_label("Add Beds")

        txt_from = wx.TextCtrl(dlg)
        txt_to = wx.TextCtrl(dlg)

        sizer = wx.FlexGridSizer(2, 2, 2, 2)
        sizer.AddMany([
            (wx.StaticText(dlg, label="From"), 0, wx.ALIGN_CENTER_VERTICAL),
            (txt_from, 0, wx.EXPAND),
            (wx.StaticText(dlg, label="To"), 0, wx.ALIGN_CENTER_VERTICAL),
            (txt_to, 0, wx.EXPAND),
        ])
        sizer.AddGrowableCol(1)
        dlg.add_to_sizer(sizer, 0, wx.EXPAND)

        dlg.CenterOnParent()
        dlg.ShowModal()

        if dlg.GetReturnCode() != wx.ID_OK:
            return

        try:
            int_from = int(txt_from.GetValue())
            int_to = int(txt_to.GetValue())
        except ValueError:
            print "Invalid Values"
            return

        if int_to < int_from:
            print "Invalid Values"
            return

        try:
            for bed_no in range(int_from, int_to + 1):
                new_bed = db.Bed()
                new_bed.number = "{}".format(bed_no)
                new_bed.ward = self.selected_item
                self.session.add(new_bed)
        except Exception as e:
            self.session.rollback()
            with wx.MessageDialog(None,
                "Error Occured. {}".format(e.message),
                "Error",
                wx.OK | wx.ICON_EXCLAMATION) as err_dlg:
                err_dlg.ShowModal()
        else:
            self.session.commit()

        self.set_selected_item(self.selected_item)


    def set_selected_item(self, item):
        super(WardEditor, self).set_selected_item(item)

        if item is None:
            self.beds_grid.Hide()
            return

        result = self.session.query(db.Bed)\
                    .filter(db.Bed.ward == item)

        self.beds_grid.set_result(result)
        self.beds_grid.Show()
        self._left_panel.Layout()

