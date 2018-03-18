"""Measurements Panel"""
import wx

from ... import database as db
from .. import images
from .. import events
from ..widgets import DbQueryResultGrid, GridColumnDateTime, GridColumnFloat
from ..dbform import FormDialog, DateTimeField, FloatField
from .encounternotebookpage import EncounterNotebookPage


class MeasurementsPanel(EncounterNotebookPage):
    """Measurements Panel"""
    def __init__(self, parent, session, **kwds):
        super(MeasurementsPanel, self).__init__(parent, session, **kwds)

        #self.session = session
        #self.encounter = None

        #self.editable = True

        #self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)

        self.toolbar.AddTool(wx.ID_ADD, "Add", images.get("add"), wx.NullBitmap, wx.ITEM_NORMAL, "Add", "")
        self.toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)

        self.toolbar.Realize()
        
        self.measurements_grid = DbQueryResultGrid(self, session)
        self.measurements_grid.add_column(GridColumnDateTime("Time", 'record_time', editable=True, width=120))
        self.measurements_grid.add_column(GridColumnFloat("Weight (kg)", 'weight', precision=1, editable=True))
        self.measurements_grid.add_column(GridColumnFloat("Height (m)", 'height', precision=2, editable=True))
        self.measurements_grid.add_column(GridColumnFloat(u"BMI (kg/m\u00B2)", 'bmi', precision=2, editable=False))
        self.measurements_grid.Bind(events.EVT_AM_DB_GRID_CELL_CHANGED, self._on_grid_changed)

        #sizer = wx.BoxSizer(wx.VERTICAL)
        #sizer.Add(self.toolbar, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        self.sizer.Add(self.measurements_grid, 1, wx.EXPAND | wx.ALL, border=5)
        #self.SetSizer(sizer)


    def _on_add(self, event):
        fields = [
            DateTimeField("Time", 'record_time', required=True),
            FloatField("Weight (kg)", 'weight'),
            FloatField("Height (m)", 'height')
        ]
        with FormDialog(self, db.Measurements, fields, size=(500, 150), title="Add Measurement") as dlg:
            dlg.CenterOnParent()
            if dlg.ShowModal() == wx.ID_OK:
                new_measurement = dlg.get_object()
                self.encounter.add_child_encounter(new_measurement)
                self.session.add(new_measurement)
                self.session.commit()
                self.set_encounter(self.encounter)
                event = events.PatientInfoChangedEvent(events.ID_PATIENT_INFO_CHANGED, object=self.encounter)
                wx.PostEvent(self, event)


    def _on_grid_changed(self, event):
        event = events.PatientInfoChangedEvent(events.ID_PATIENT_INFO_CHANGED, object=event.object)
        wx.PostEvent(self, event)


    def editable_on(self):
        super(MeasurementsPanel, self).editable_on()
        self.measurements_grid.EnableEditing(True)

    
    def editable_off(self):
        super(MeasurementsPanel, self).editable_off()
        self.measurements_grid.EnableEditing(False)


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing.
          Always false in this panel as all changes are autosaved"""
        return False


    def save_changes(self):
        """Save changes. Everything is auto saved."""
        pass


    def set_encounter(self, encounter):
        """Set the current encounter"""
        super(MeasurementsPanel, self).set_encounter(encounter)

        query_result = self.session.query(db.Measurements)\
                            .filter(db.Measurements.parent_id == self.encounter.id)\
                            .order_by(db.Measurements.start_time.desc())

        self.measurements_grid.set_result(query_result)