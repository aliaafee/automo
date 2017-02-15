import wx
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from ObjectListView import ObjectListView, ColumnDefn
import tempfile

from objectlistviewmod import ObjectListViewMod, EVT_OVL_CHECK_EVENT
from images import *
from database import Patient
from pdfviewer import PDFViewer
from printing import *


class PatientListPanel(wx.Panel):
    def __init__(self, parent, session, **kwds):
        super(PatientListPanel, self).__init__(parent, **kwds)

        self.session = session

        self.patientPanel = None
        self.selectedPatient = None

        sizer = wx.BoxSizer(wx.VERTICAL)

        toolbar = wx.ToolBar(self, style=wx.TB_NODIVIDER)

        tbAddPatient = toolbar.AddLabelTool(
                wx.ID_ANY, 'Add Patient',  BitmapFromBase64(toolbar_add_b64))
        self.Bind(wx.EVT_TOOL, self.OnAddPatient, tbAddPatient)

        tbRemovePatient = toolbar.AddLabelTool(
                wx.ID_ANY, 'Remove Patient',  BitmapFromBase64(toolbar_remove_b64))
        self.Bind(wx.EVT_TOOL, self.OnRemovePatient, tbRemovePatient)

        tbPrintList = toolbar.AddLabelTool(
                wx.ID_ANY, 'Print Patients List',  BitmapFromBase64(toolbar_print_list_b64))
        self.Bind(wx.EVT_TOOL, self.OnPrintList, tbPrintList)

        tbPrintAll = toolbar.AddLabelTool(
                wx.ID_ANY, 'Print All Prescriptions',  BitmapFromBase64(toolbar_print_all_b64))
        self.Bind(wx.EVT_TOOL, self.OnPrintAll, tbPrintAll)

        toolbar.Realize()

        sizer.Add(toolbar, 0, wx.ALL | wx. EXPAND)

        self.patientList = ObjectListViewMod(self, style=wx.LC_REPORT)
        
        #userImage = self.patientList.AddImages(BitmapFromBase64(patient_16_b64), BitmapFromBase64(patient_32_b64)) #getUser32Bitmap())        
        
        self.patientList.SetColumns([
            #ColumnDefn("Bed", "left", 70, "bed_no", imageGetter=userImage),
            ColumnDefn("Bed", "left", 70, "bed_no"),
            ColumnDefn("Hospital No", "left", 70, "hospital_no"),
            ColumnDefn("Name", "left", 140, "name")
        ])
        
        self.patientList.SetEmptyListMsg("")
        self.patientList.useAlternateBackColors = False
        self.patientList.CreateCheckStateColumn()

        self.patientList.Bind(EVT_OVL_CHECK_EVENT, self.OnPatientCheck)
        self.patientList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnPatientContextMenu)
        self.patientList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnPatientSelected)

        sizer.Add(self.patientList, 1, wx.ALL | wx. EXPAND, border=10)

        self.SetSizer(sizer)

        self.patientMenu = wx.Menu()
        id = 600
        self.patientMenu.Append(id, "Remove", "Remove Patient")
        wx.EVT_MENU(self, id,  self.OnRemovePatient)
        id = 601
        self.patientMenu.Append(id, "Tick All", "Tick All Patients")
        wx.EVT_MENU(self, id,  self.OnTickAllPatients)
        id = 602
        self.patientMenu.Append(id, "Untick All", "Untick All Patients")
        wx.EVT_MENU(self, id,  self.OnUntickAllPatients)


    def OnAddPatient(self, event):
        new_pt = Patient(
            active = True, 
            bed_no = "", 
            hospital_no="", 
            national_id_no="", 
            name="", 
            age="", 
            sex="", 
            diagnosis=""
        )
        
        self.session.add(new_pt)
        self.session.commit()

        self.UpdateList()

        self.selectedPatient = new_pt
        
        self.patientPanel.set(self.selectedPatient)
        self.patientList.SelectObject(self.selectedPatient)

        self.patientPanel.txtBed.SetFocus()
        self.patientPanel.txtBed.SetSelection(-1,-1)


    def OnRemovePatient(self, event):
        selectedPatients = self.patientList.GetSelectedObjects()

        if len(selectedPatients) < 1:
            return

        dlg = wx.MessageDialog(None, 'Remove selected patients?', 'Question', 
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        result = dlg.ShowModal()

        if (result != wx.ID_YES):
            return

        self.patientPanel.unSet()

        for patient in selectedPatients:
            self.session.delete(patient)

        self.session.commit()

        self.UpdateList()


    def OnPatientCheck(self, event):
        if event.value == True:
            event.object.active = True
        else:
            event.object.active = False
        self.session.commit()


    def OnPatientContextMenu(self, event):
        self.PopupMenu(self.patientMenu)


    def OnTickAllPatients(self, event):
        patients = self.patientList.GetObjects()
        for patient in patients:
            patient.active = True
            self.patientList.SetCheckState(patient, True)

        self.session.commit()
        self.patientList.RefreshObjects(patients)


    def OnUntickAllPatients(self, event):
        patients = self.patientList.GetObjects()
        for patient in patients:
            patient.active = False
            self.patientList.SetCheckState(patient, False)

        self.session.commit()
        self.patientList.RefreshObjects(patients)


    def OnPrintAll(self, event):
        tempFile = tempfile.mktemp(".pdf")

        GenerateAllPrescriptions(self.session, tempFile)

        pdfV = PDFViewer(None, title="Print Preview")
        pdfV.viewer.UsePrintDirect = ``False``
        pdfV.viewer.LoadFile(tempFile)
        pdfV.Show()


    def OnPrintList(self, event):
        tempFile = tempfile.mktemp(".pdf")

        GeneratePatientList(self.session, tempFile)

        pdfV = PDFViewer(None, title="Print Preview")
        pdfV.viewer.UsePrintDirect = ``False``
        pdfV.viewer.LoadFile(tempFile)
        pdfV.Show()


    def OnPatientSelected(self, event):
        listSelected = self.patientList.GetSelectedObject()

        if listSelected == None:
            self.selectedPatient = None
            self.patientPanel.unSet()
            return

        self.selectedPatient = listSelected
        
        self.patientPanel.set(self.selectedPatient)


    def UpdateList(self):
        self.patientList.DeleteAllItems ()
        
        for patient in self.session.query(Patient).order_by(Patient.bed_no):
            self.patientList.AddObject(patient)
            if patient.active:
                self.patientList.SetCheckState(patient, True)
            else:
                self.patientList.SetCheckState(patient, False)

        self.patientList.RefreshObjects(self.patientList.GetObjects())

