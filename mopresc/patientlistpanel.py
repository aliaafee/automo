import wx
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas

from images import *
from database import Patient
from pdfviewer import PDFViewer
from generateprescription import GeneratePrescription


class PatientListPanel(wx.Panel):
    def __init__(self, parent, session, **kwds):
        super(PatientListPanel, self).__init__(parent, **kwds)

        self.session = session

        self.patientPanel = None
        self.selectedPatient = None
        self.selectedListIndex = None
        self.patients = []

        sizer = wx.BoxSizer(wx.VERTICAL)

        toolbar = wx.ToolBar(self, style=wx.TB_NODIVIDER)

        tbAddPatient = toolbar.AddLabelTool(
                wx.ID_ANY, 'Add Patient',  BitmapFromBase64(toolbar_add_b64))
        self.Bind(wx.EVT_TOOL, self.OnAddPatient, tbAddPatient)

        tbRemovePatient = toolbar.AddLabelTool(
                wx.ID_ANY, 'Remove Patient',  BitmapFromBase64(toolbar_remove_b64))
        self.Bind(wx.EVT_TOOL, self.OnRemovePatient, tbRemovePatient)

        tbPrintAll = toolbar.AddLabelTool(
                wx.ID_ANY, 'Print All',  BitmapFromBase64(toolbar_print_b64))
        self.Bind(wx.EVT_TOOL, self.OnPrintAll, tbPrintAll)

        toolbar.Realize()

        sizer.Add(toolbar, 0, wx.ALL | wx. EXPAND)

        self.patientList = wx.ListCtrl(self, size=(-1,100),style=wx.LC_REPORT)
        self.patientList.InsertColumn(0, 'Bed')
        self.patientList.InsertColumn(1, 'Hospital No')
        self.patientList.InsertColumn(2, 'Name')
        self.patientList.SetColumnWidth(0, 50)
        self.patientList.SetColumnWidth(2, 140)
        self.patientList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnPatientSelected)

        sizer.Add(self.patientList, 1, wx.ALL | wx. EXPAND, border=10)

        self.SetSizer(sizer)


    def OnAddPatient(self, event):
        """
        dlg = wx.TextEntryDialog(self, "Bed Number", defaultValue="")
        dlg.ShowModal()
        value = dlg.GetValue()
        dlg.Destroy()

        if value == "":
            return
        """

        new_pt = Patient(bed_no = "", hospital_no="", national_id_no="", name="", age="", sex="", diagnosis="")
        self.session.add(new_pt)
        self.session.commit()

        self.UpdateList()

        self.selectedPatient = new_pt
        self.selectedListIndex = self.patientList.GetItemCount() - 1
        
        self.patientPanel.set(self.selectedPatient, self.selectedListIndex)
        self.patientList.SetItemState(self.selectedListIndex, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)

        self.patientPanel.txtBed.SetFocus()

        #Deselect item (wxLIST_STATE_FOCUSED - dotted border)
        #wxListCtrl->SetItemState(item, 0, wxLIST_STATE_SELECTED|wxLIST_STATE_FOCUSED);


    def OnRemovePatient(self, event):
        self.patientPanel.unSet()

        self.session.delete(self.selectedPatient)
        self.session.commit()

        self.selectedPatient = None
        self.selectedListIndex = None

        self.UpdateList()
        print "Remove Patient"


    def OnPrintAll(self, event):
        c = canvas.Canvas("print.pdf", pagesize=A5)
        for patient in self.session.query(Patient).order_by(Patient.id):
            GeneratePrescription(patient, c)
        c.save()

        pdfV = PDFViewer(None)
        pdfV.viewer.UsePrintDirect = ``False``
        pdfV.viewer.LoadFile("print.pdf")
        pdfV.Show()


    def OnPatientSelected(self, event):
        self.selectedPatient = self.patients[event.Index]
        self.selectedListIndex = event.Index
        self.patientPanel.set(self.selectedPatient, self.selectedListIndex)


    def UpdateList(self):
        self.patientList.DeleteAllItems ()
        
        self.patients = []
        index = 0
        for patient in self.session.query(Patient).order_by(Patient.id):
            self.patientList.InsertStringItem(index, str(patient.bed_no))
            self.patientList.SetStringItem(index, 1, str(patient.hospital_no))
            self.patientList.SetStringItem(index, 2, str(patient.name))
            self.patients.append(patient)
            index += 1
