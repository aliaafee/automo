"""Vital Signs Panel"""
import wx

from .. import database as db
from . import images
from .widgets import DbQueryResultGrid, GridColumnDateTime, GridColumnFloat
from .dbform import FormDialog, DateTimeField, FloatField


class VitalsPanel(wx.Panel):
    """Vital Signs Panel"""
    def __init__(self, parent, session, **kwds):
        super(VitalsPanel, self).__init__(parent, **kwds)

        self.session = session
        self.encounter = None

        self.editable = True

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)

        self.toolbar.AddTool(wx.ID_ADD, "Add", images.get("add"), wx.NullBitmap, wx.ITEM_NORMAL, "Add", "")
        self.toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)

        self.toolbar.Realize()
        
        self.vitals_grid = DbQueryResultGrid(self, session)
        self.vitals_grid.add_column(GridColumnDateTime("Time", 'record_time', editable=True, width=120))
        self.vitals_grid.add_column(GridColumnFloat("Pulse (bmp)", 'pulse_rate', precision=0, editable=True))
        self.vitals_grid.add_column(GridColumnFloat("Resp (bmp)", 'respiratory_rate', precision=0, editable=True))
        self.vitals_grid.add_column(GridColumnFloat("SBP (mmHg)", 'systolic_bp', precision=0, editable=True))
        self.vitals_grid.add_column(GridColumnFloat("DBP (mmHg)", 'diastolic_bp', precision=0, editable=True))
        self.vitals_grid.add_column(GridColumnFloat(u"Temp (\u00B0C)", 'temperature', precision=1, editable=True))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolbar, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        sizer.Add(self.vitals_grid, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(sizer)


    def _on_add(self, event):
        fields = [
            DateTimeField("Time", 'record_time', required=True),
            FloatField("Pulse (bmp)", 'pulse_rate'),
            FloatField("Resp (bmp)", 'respiratory_rate'),
            FloatField("SBP (mmHg)", 'systolic_bp'),
            FloatField("DBP (mmHg)", 'diastolic_bp'),
            FloatField(u"Temp (\u00B0C)", 'temperature')
        ]
        with FormDialog(self, db.VitalSigns, fields, size=(500, 200), title="Add Vital Signs") as dlg:
            dlg.CenterOnParent()
            if dlg.ShowModal() == wx.ID_OK:
                new_vitals = dlg.get_object()
                self.encounter.add_child_encounter(new_vitals)
                self.session.add(new_vitals)
                self.session.commit()
                self.set_encounter(self.encounter)


    def set_editable(self, editable):
        """Set control to editable or not"""
        if editable:
            self.toolbar.Show()
            self.vitals_grid.EnableEditing(True)
        else:
            self.toolbar.Hide()
            self.vitals_grid.EnableEditing(False)

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

        query_result = self.session.query(db.VitalSigns)\
                            .filter(db.VitalSigns.parent_id == self.encounter.id)\
                            .order_by(db.VitalSigns.start_time.desc())

        self.vitals_grid.set_result(query_result)
