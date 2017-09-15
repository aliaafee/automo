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
        self.toolbar.AddLabelTool(ID_IMPORT_PATIENTS, "Import Patients", images.get("add"),
                                  wx.NullBitmap, wx.ITEM_NORMAL, "Import Patients", "")
        self.toolbar.AddSeparator()
        super(CWardInterface, self).create_toolbar()


    def create_tool_menu(self):
        self.tool_menu.Append(ID_IMPORT_PATIENTS, "Import Patients", "Import Patients")
        wx.EVT_MENU(self, ID_IMPORT_PATIENTS, self._on_import)
        self.tool_menu.AppendSeparator()
        super(CWardInterface, self).create_tool_menu()


    def _on_import(self, event):
        with BatchPatientImporter(self, self.session) as importer:
            importer.CenterOnScreen()
            importer.ShowModal()
