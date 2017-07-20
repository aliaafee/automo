"""AutoMO Events"""
import wx.lib.newevent

"""Emitted when value of DbDatePicker, DbRelationCtrl, DbRichTextCtrl, DbTextCtrl is changed"""
DbCtrChangedEvent, EVT_AM_DB_CTRL_CHANGED_EVENT = wx.lib.newevent.NewEvent()

"""Emitter by Admission Panel when admission is changed"""
AdmissionChangedEvent, EVT_AM_ADMISSION_CHANGED_EVENT = wx.lib.newevent.NewEvent()

"""Emitted by condition panel when conditions are changed"""
ConditionChangedEvent, EVT_AM_CONDITION_CHANGED_EVENT = wx.lib.newevent.NewEvent()


