"""Settings Frame"""
import wx

from .. import database as db
from .basedialog import BaseDialog
from . import images
from .configeditor import ConfigEditor
from .listformeditor import ListFormEditor
from .wardeditor import WardEditor
from .dbform import DbStringField, DbCheckBoxField


class SettingsDialog(wx.Dialog):
    """Setting Frame"""
    def __init__(self, parent, session, size=(600, 500), **kwds):
        super(SettingsDialog, self).__init__(parent, size=size, 
              style=wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION, **kwds)
        
        self.SetTitle("AutoMO Settings")

        self.session = session

        self.listbook = wx.Notebook(self)

        fields = [
            DbStringField("Record Card No.", 'record_card_no'),
            DbStringField("Name", 'name'),
            DbStringField("PMR Number", 'pmr_no'),
            DbCheckBoxField("Active", 'active')
        ]
        doctor_editor = ListFormEditor(self.listbook, self.session, db.Doctor, fields)
        self.listbook.AddPage(doctor_editor, "Doctors")

        ward_editor = WardEditor(self.listbook, self.session)
        self.listbook.AddPage(ward_editor, "Ward and Beds")

        config_editor = ConfigEditor(self.listbook)
        self.listbook.AddPage(config_editor, "Configuration")

        sizer = wx.BoxSizer()
        sizer.Add(self.listbook, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(sizer)
