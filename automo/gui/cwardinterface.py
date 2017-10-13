"""C Ward Interface"""
import wx

from . import images
from .wardinterface import WardInterface
from .batchpatientimporter import BatchPatientImporter

ID_IMPORT_PATIENTS = wx.NewId()


class CWardInterface(WardInterface):
    def __init__(self, parent, session=None):
        super(CWardInterface, self).__init__(parent, session)

        self.set_title("Circumcision Ward")


    def create_toolbar(self):
        super(CWardInterface, self).create_toolbar()
        self.toolbar.AddSeparator()
        self.toolbar.AddTool(ID_IMPORT_PATIENTS, "Batch Import Patients", images.get("new_patient_many"),
                                  wx.NullBitmap, wx.ITEM_NORMAL, "Batch Import Patients", "")


    def create_tool_menu(self):
        self.tool_menu.Append(ID_IMPORT_PATIENTS, "Import Patients", "Import Patients")
        self.Bind(wx.EVT_MENU, self._on_import, id=ID_IMPORT_PATIENTS)
        self.tool_menu.AppendSeparator()
        super(CWardInterface, self).create_tool_menu()


    def _on_import(self, event):
        with BatchPatientImporter(self, self.session) as importer:
            importer.CenterOnScreen()
            importer.ShowModal()
