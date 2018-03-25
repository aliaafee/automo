"""Settings Frame"""
import wx

from ... import database as db
from ..basedialog import BaseDialog
from .. import images
from ..dbform import StringField, CheckBoxField
from .configeditor import ConfigEditor
from .listformeditor import ListFormEditor
from .wardeditor import WardEditor
from .drughistoryeditor import DrugHistoryEditor


class SettingsDialog(wx.Dialog):
    """Setting Frame"""
    def __init__(self, parent, session, size=(600, 500), **kwds):
        super(SettingsDialog, self).__init__(parent, size=size, 
              style=wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION, **kwds)
        
        self.SetTitle("AutoMO Settings")

        self.session = session

        self.listbook = wx.Notebook(self)

        fields = [
            StringField("Record Card No.", 'record_card_no'),
            StringField("Name", 'name'),
            StringField("PMR Number", 'pmr_no'),
            CheckBoxField("Active", 'active')
        ]
        doctor_editor = ListFormEditor(self.listbook, self.session, db.Doctor, fields)
        self.listbook.AddPage(doctor_editor, "Consultants")

        fields = [
            StringField("Record Card No.", 'record_card_no'),
            StringField("Name", 'name'),
            StringField("PMR Number", 'pmr_no'),
            CheckBoxField("Active", 'active')
        ]
        mo_editor = ListFormEditor(self.listbook, self.session, db.MedicalOfficer, fields)
        self.listbook.AddPage(mo_editor, "Medical Officers")

        ward_editor = WardEditor(self.listbook, self.session)
        self.listbook.AddPage(ward_editor, "Ward and Beds")

        drug_history = DrugHistoryEditor(self.listbook, self.session)
        self.listbook.AddPage(drug_history, "Drugs")

        config_editor = ConfigEditor(self.listbook)
        self.listbook.AddPage(config_editor, "Configuration")

        sizer = wx.BoxSizer()
        sizer.Add(self.listbook, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(sizer)
