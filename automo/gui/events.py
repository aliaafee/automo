"""AutoMO Events"""
import wx.lib.newevent

"""Emitted when value of DbDatePicker, DbRelationCtrl, DbRichTextCtrl, DbTextCtrl is changed"""
DbCtrlChangedEvent, EVT_AM_DB_CTRL_CHANGED = wx.lib.newevent.NewEvent()

"""Emitted when DbQueryResultGrid cell is changed, contains the object that was changed"""
DbGridCellChangedEvent, EVT_AM_DB_GRID_CELL_CHANGED = wx.lib.newevent.NewEvent()

"""Emitted when field is DbForm changed, returned object is the field class"""
DbFormChangedEvent, EVT_AM_DB_FORM_CHANGED = wx.lib.newevent.NewEvent()

"""Emitted by Encounter Panel when encounter is changed"""
EncounterChangedEvent, EVT_AM_ENCOUNTER_CHANGED = wx.lib.newevent.NewCommandEvent()
ID_ENCOUNTER_CHANGED = wx.NewId()

"""Emitted by Measurement Panel when measurement is changed"""
MeasurementChangedEvent, EVT_AM_MEASUREMENT_CHANGED = wx.lib.newevent.NewEvent()

"""Emitted when Patient Information changed from encounter panel"""
PatientInfoChangedEvent, EVT_AM_PATIENT_INFO_CHANGED  = wx.lib.newevent.NewCommandEvent()
ID_PATIENT_INFO_CHANGED = wx.NewId()

"""Emitted when patient selection changed"""
PatientSelectedEvent, EVT_AM_PATIENT_SELECTED = wx.lib.newevent.NewCommandEvent()
ID_PATIENT_SELECTED = wx.NewId()