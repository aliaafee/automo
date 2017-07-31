"""AutoMO Events"""
import wx.lib.newevent

"""Emitted when value of DbDatePicker, DbRelationCtrl, DbRichTextCtrl, DbTextCtrl is changed"""
DbCtrChangedEvent, EVT_AM_DB_CTRL_CHANGED = wx.lib.newevent.NewEvent()

"""Emitter by Admission Panel when admission is changed"""
AdmissionChangedEvent, EVT_AM_ADMISSION_CHANGED = wx.lib.newevent.NewEvent()

"""Emitted by condition panel when conditions are changed"""
ConditionChangedEvent, EVT_AM_CONDITION_CHANGED = wx.lib.newevent.NewEvent()

"""Emitted when patient selection changed"""
PatientChangedEvent, EVT_AM_PATIENT_CHANGED = wx.lib.newevent.NewEvent()
