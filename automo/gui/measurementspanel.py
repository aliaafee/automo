"""Measurements Panel"""
import wx

from .. import database as db
from . import images
from .dbqueryresultgrid import DbQueryResultGrid, GridColumnDateTime, GridColumnFloat


class MeasurementsPanel(wx.Panel):
    """Measurements Panel"""
    def __init__(self, parent, session, **kwds):
        super(MeasurementsPanel, self).__init__(parent, **kwds)

        self.session = session
        self.encounter = None

        self.editable = True

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)

        self.toolbar.AddLabelTool(wx.ID_ADD, "Add", images.get("add"), wx.NullBitmap, wx.ITEM_NORMAL, "Add", "")

        self.toolbar.Realize()
        
        self.measurements_grid = DbQueryResultGrid(self, session)
        self.measurements_grid.add_column(GridColumnDateTime("Time", 'record_time', editable=True, width=120))
        self.measurements_grid.add_column(GridColumnFloat("Weight (kg)", 'weight', precision=1, editable=True))
        self.measurements_grid.add_column(GridColumnFloat("Height (m)", 'height', precision=2, editable=True))
        self.measurements_grid.add_column(GridColumnFloat(u"BMI (kg/m\u00B2)", 'bmi', precision=2, editable=False))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolbar, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        sizer.Add(self.measurements_grid, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(sizer)


    def set_editable(self, editable):
        """Set control to editable or not"""
        if editable:
            self.toolbar.Show()
        else:
            self.toolbar.Hide()

        if self.editable != editable:
            self.Layout()

        self.editable = editable


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing.
          Always false in this panel as all changes are autosaved"""
        return False


    def save_changes(self):
        """Save changes. Everything is auto saved."""
        pass


    def set_encounter(self, encounter):
        """Set the current encounter"""
        self.encounter = encounter

        query_result = self.session.query(db.Measurements)\
                            .filter(db.Measurements.parent_id == self.encounter.id)\
                            .order_by(db.Measurements.start_time.desc())

        self.measurements_grid.set_result(query_result)
