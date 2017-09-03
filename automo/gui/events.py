"""AutoMO Events"""
import wx.lib.newevent

"""Emitted when value of DbDatePicker, DbRelationCtrl, DbRichTextCtrl, DbTextCtrl is changed"""
DbCtrlChangedEvent, EVT_AM_DB_CTRL_CHANGED = wx.lib.newevent.NewEvent()

"""Emitter by Encounter Panel when encounter is changed"""
EncounterChangedEvent, EVT_AM_ENCOUNTER_CHANGED = wx.lib.newevent.NewEvent()

"""Emitted by problem panel when problems are changed"""
ProblemChangedEvent, EVT_AM_PROBLEM_CHANGED = wx.lib.newevent.NewEvent()

"""Emitted when patient selection changed"""
PatientChangedEvent, EVT_AM_PATIENT_CHANGED = wx.lib.newevent.NewEvent()
