import wx
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from ObjectListView import ObjectListView, ColumnDefn, OLVEvent
import tempfile

from images import *
from objectlistviewmod import ObjectListViewMod, EVT_OVL_CHECK_EVENT
from pdfviewer import PDFViewer
from printing import *
from drugaddpanel import DrugAddPanel


class PatientPanel(wx.Panel):
    def __init__(self, parent, session, **kwds):
        super(PatientPanel, self).__init__(parent, **kwds)
        
        self.session = session
        self.patientListPanel = None

        self.patient = None

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = wx.ToolBar(self, style=wx.TB_NODIVIDER)

        tbPrint = self.toolbar.AddLabelTool(
                wx.ID_ANY, 'Print Prescription',  BitmapFromBase64(toolbar_print_one_b64))
        self.Bind(wx.EVT_TOOL, self.OnPrint, tbPrint)

        self.toolbar.Realize()

        sizer.Add(self.toolbar, 0, wx.ALL | wx. EXPAND)

        gridSizer = wx.FlexGridSizer(8,2,5,5)
        gridSizer.AddGrowableCol(1,1)

        labelWidth = 100

        self.lblBed = wx.StaticText(self, label='Bed', size=wx.Size(labelWidth,-1))
	self.txtBed = wx.TextCtrl(self)
	gridSizer.Add(self.lblBed, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
	gridSizer.Add(self.txtBed, 1, wx.EXPAND)
        self.txtBed.Bind(wx.EVT_TEXT, self.OnChange)
        
        self.lblHospitalNo = wx.StaticText(self, label='Hospital No', size=wx.Size(labelWidth,-1))
	self.txtHospitalNo = wx.TextCtrl(self)
	gridSizer.Add(self.lblHospitalNo, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
	gridSizer.Add(self.txtHospitalNo, 1, wx.EXPAND)
        self.txtHospitalNo.Bind(wx.EVT_TEXT, self.OnChange)

        self.lblNationalIdNo = wx.StaticText(self, label='National Id No', size=wx.Size(labelWidth,-1))
	self.txtNationalIdNo = wx.TextCtrl(self)
	gridSizer.Add(self.lblNationalIdNo, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
	gridSizer.Add(self.txtNationalIdNo, 1, wx.EXPAND)
        self.txtNationalIdNo.Bind(wx.EVT_TEXT, self.OnChange)

        self.lblName = wx.StaticText(self, label='Name', size=wx.Size(labelWidth,-1))
	self.txtName = wx.TextCtrl(self)
	gridSizer.Add(self.lblName, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
	gridSizer.Add(self.txtName, 1, wx.EXPAND)
        self.txtName.Bind(wx.EVT_TEXT, self.OnChange)
        
        self.lblAge = wx.StaticText(self, label='Age', size=wx.Size(labelWidth,-1))
	self.txtAge = wx.TextCtrl(self)
	gridSizer.Add(self.lblAge, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
	gridSizer.Add(self.txtAge, 1, wx.EXPAND)
        self.txtAge.Bind(wx.EVT_TEXT, self.OnChange)

        self.lblSex = wx.StaticText(self, label='Sex', size=wx.Size(labelWidth,-1))
	self.txtSex = wx.TextCtrl(self)
	gridSizer.Add(self.lblSex, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
	gridSizer.Add(self.txtSex, 1, wx.EXPAND)
        self.txtSex.Bind(wx.EVT_TEXT, self.OnChange)

        self.lblDiagnosis = wx.StaticText(self, label='Diagnosis', size=wx.Size(labelWidth,-1))
	self.txtDiagnosis = wx.TextCtrl(self)
	gridSizer.Add(self.lblDiagnosis, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
	gridSizer.Add(self.txtDiagnosis, 1, wx.EXPAND)
        self.txtDiagnosis.Bind(wx.EVT_TEXT, self.OnChange)

        sizer.Add(gridSizer, 0, wx.ALL | wx.EXPAND, border=10)

        self.txtDrugName = DrugAddPanel(self, session, self)
        sizer.Add(self.txtDrugName, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, border=10)

        self.prescriptionList = ObjectListViewMod( 
                self, 
                style=wx.LC_REPORT|wx.SUNKEN_BORDER, 
                cellEditMode=ObjectListView.CELLEDIT_DOUBLECLICK 
        )

        self.prescriptionList.SetColumns([
            ColumnDefn("Drug", "left", 180, "drug_name", isEditable = False),
            ColumnDefn("Order", "left", 140, "drug_order")
        ])
        
        self.prescriptionList.SetEmptyListMsg("")
        self.prescriptionList.useAlternateBackColors = False
        self.prescriptionList.CreateCheckStateColumn()

        self.prescriptionList.Bind(EVT_OVL_CHECK_EVENT, self.OnRxCheck)
        self.prescriptionList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnRxContextMenu)
        self.prescriptionList.Bind(OLVEvent.EVT_CELL_EDIT_FINISHED, self.OnCellEditFinished)

        sizer.Add(self.prescriptionList, 1, wx.RIGHT | wx.LEFT | wx.BOTTOM | wx. EXPAND, border=10)

        #Enter Treversal
        self.txtBed.Bind(wx.EVT_KEY_UP, self.OntxtBedKeyUp)
        self.txtHospitalNo.Bind(wx.EVT_KEY_UP, self.OntxtHospitalNoKeyUp)
        self.txtNationalIdNo.Bind(wx.EVT_KEY_UP, self.OntxtNationalIdNoKeyUp)
        self.txtName.Bind(wx.EVT_KEY_UP, self.OntxtNameKeyUp)
        self.txtAge.Bind(wx.EVT_KEY_UP, self.OntxtAgeKeyUp)
        self.txtSex.Bind(wx.EVT_KEY_UP, self.OntxtSexKeyUp)
        self.txtDiagnosis.Bind(wx.EVT_KEY_UP, self.OntxtDiagnosisKeyUp)
        
        self.SetSizer(sizer)

        self.rxMenu = wx.Menu()
        id = 500
        self.rxMenu.Append(id, "Remove", "Remove Medication.")
        wx.EVT_MENU(self, id,  self.OnRemoveRx)

        self.unSet()


    def set(self, patient):
        self.patient = patient

        self.txtHospitalNo.ChangeValue(str(patient.hospital_no))
        self.txtNationalIdNo.ChangeValue(str(patient.national_id_no))
        self.txtBed.ChangeValue(str(patient.bed_no))
        self.txtName.ChangeValue(str(patient.name))
        self.txtAge.ChangeValue(str(patient.age))
        self.txtSex.ChangeValue(str(patient.sex))
        self.txtDiagnosis.ChangeValue(str(patient.diagnosis))

        self.updateRx()

        self.Enable()


    def unSet(self):
        self.patient = None

        self.txtHospitalNo.ChangeValue("")
        self.txtNationalIdNo.ChangeValue("")
        self.txtBed.ChangeValue("")
        self.txtName.ChangeValue("")
        self.txtAge.ChangeValue("")
        self.txtSex.ChangeValue("")
        self.txtDiagnosis.ChangeValue("")

        self.prescriptionList.DeleteAllItems()

        self.Disable()
        

    def updateRx(self):
        self.prescriptionList.DeleteAllItems()

        for row in self.patient.rxs:
            self.prescriptionList.AddObject(row)
            if row.active:
                self.prescriptionList.SetCheckState(row, True)
            else:
                self.prescriptionList.SetCheckState(row, False)

        self.prescriptionList.RefreshObjects(self.prescriptionList.GetObjects())


    def OnChange(self, event):
        self.patient.hospital_no = str(self.txtHospitalNo.GetValue())
        self.patient.national_id_no = str(self.txtNationalIdNo.GetValue())
        self.patient.bed_no = str(self.txtBed.GetValue())
        self.patient.name = str(self.txtName.GetValue())
        self.patient.age = str(self.txtAge.GetValue())
        self.patient.sex = str(self.txtSex.GetValue())
        self.patient.diagnosis = str(self.txtDiagnosis.GetValue())
        
        self.patientListPanel.patientList.RefreshObjects([self.patient])

        self.session.commit()


    def OnCellEditFinished(self, event):
        self.session.commit()


    def OntxtBedKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txtHospitalNo.SetFocus()
            self.txtHospitalNo.SetSelection(-1,-1)
            

    def OntxtHospitalNoKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txtNationalIdNo.SetFocus()
            self.txtNationalIdNo.SetSelection(-1,-1)

    
    def OntxtNationalIdNoKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txtName.SetFocus()
            self.txtName.SetSelection(-1,-1)

    
    def OntxtNameKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txtAge.SetFocus()
            self.txtAge.SetSelection(-1,-1)

    
    def OntxtAgeKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txtSex.SetFocus()
            self.txtSex.SetSelection(-1,-1)

    
    def OntxtSexKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txtDiagnosis.SetFocus()
            self.txtDiagnosis.SetSelection(-1,-1)

   
    def OntxtDiagnosisKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txtDrugName.txtDrugName.SetFocus()


    def OnRxCheck(self, event):
        if event.value == True:
            event.object.active = True
        else:
            event.object.active = False
        self.session.commit()


    def OnRxContextMenu(self, event):
        self.PopupMenu(self.rxMenu)


    def OnRemoveRx(self, event):
        dlg = wx.MessageDialog(None, 'Remove selected medications?', 'Question', 
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        result = dlg.ShowModal()

        if (result != wx.ID_YES):
            return

        for rx in self.prescriptionList.GetSelectedObjects():
            self.session.delete(rx)

        self.session.commit()

        self.updateRx()
    

    def OnPrint(self, event):
        if self.patient == None:
            return
        
        self.session.refresh(self.patient)

        tempFile = tempfile.mktemp(".pdf")

        GeneratePrescription(self.patient, tempFile)

        pdfV = PDFViewer(None, title = "Print Preview")
        pdfV.viewer.UsePrintDirect = ``False``
        pdfV.viewer.LoadFile(tempFile)
        pdfV.Show()
