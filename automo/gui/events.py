"""AutoMO Events"""
import wx.lib.newevent

"""Emitted when value of DbDatePicker, DbRelationCtrl, DbRichTextCtrl, DbTextCtrl is changed"""
DbCtrlChangedEvent, EVT_AM_DB_CTRL_CHANGED = wx.lib.newevent.NewEvent()

"""Emitted when DbQueryResultGrid cell is changed, contains the object that was changed"""
DbGridCellChangedEvent, EVT_AM_DB_GRID_CELL_CHANGED = wx.lib.newevent.NewEvent()

"""Emitted by Encounter Panel when encounter is changed"""
EncounterChangedEvent, EVT_AM_ENCOUNTER_CHANGED = wx.lib.newevent.NewCommandEvent()
ID_ENCOUNTER_CHANGED = 98001

"""Emitted by Measurement Panel when measurement is changed"""
MeasurementChangedEvent, EVT_AM_MEASUREMENT_CHANGED = wx.lib.newevent.NewEvent()

"""Emitted when Patient Information changed from encounter panel"""
PatientInfoChangedEvent, EVT_AM_PATIENT_INFO_CHANGED  = wx.lib.newevent.NewCommandEvent()
ID_PATIENT_INFO_CHANGED = 98002

"""Emitted when patient selection changed"""
PatientChangedEvent, EVT_AM_PATIENT_CHANGED = wx.lib.newevent.NewEvent()
