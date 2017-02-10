import wx
from reportlab.lib.pagesizes import A5
from reportlab.pdfgen import canvas
from ObjectListView import ObjectListView, ColumnDefn

from images import *
from pdfviewer import PDFViewer
from grid import *
from generateprescription import GeneratePrescription
from drugaddpanel import DrugAddPanel


import  wx.lib.newevent
OvlCheckEvent, EVT_OVL_CHECK_EVENT = wx.lib.newevent.NewEvent()
class ObjectListViewCheck(ObjectListView):  
    def _HandleLeftDownOnImage(self, rowIndex, subItemIndex):
        column = self.columns[subItemIndex]
        if not column.HasCheckState():
            return

        self._PossibleFinishCellEdit()
        modelObject = self.GetObjectAt(rowIndex)
        if modelObject is not None:
            column.SetCheckState(modelObject, not column.GetCheckState(modelObject))

            # Just added the event here ===================================
            e = OvlCheckEvent(object=modelObject, value=column.GetCheckState(modelObject))
            wx.PostEvent(self, e)
            # =============================================================

            self.RefreshIndex(rowIndex, modelObject)

        
    """
    def _InitializeCheckBoxImages(self):
        print "Doing This"
        bmpChecked_16 = BitmapFromBase64(checked_16_b64)
        bmpUnchecked_16 = BitmapFromBase64(unchecked_16_b64)
        bmpChecked_32 = BitmapFromBase64(checked_32_b64)
        bmpUnchecked_32 = BitmapFromBase64(unchecked_32_b64)

        self.AddNamedImages(ObjectListView.NAME_CHECKED_IMAGE, bmpChecked_16, bmpChecked_32)
        self.AddNamedImages(ObjectListView.NAME_UNCHECKED_IMAGE, bmpUnchecked_16, bmpUnchecked_32)
        self.AddNamedImages(ObjectListView.NAME_UNDETERMINED_IMAGE, bmpUnchecked_16, bmpUnchecked_32)
    """




class PatientPanel(wx.Panel):
    def __init__(self, parent, session, **kwds):
        super(PatientPanel, self).__init__(parent, **kwds)
        
        self.session = session
        self.patientListPanel = None

        self.patient = None
        self.listIndex = None
        #self.rxs = []

        sizer = wx.BoxSizer(wx.VERTICAL)

        #Patients Toolbar
        self.toolbar = wx.ToolBar(self, style=wx.TB_NODIVIDER)

        tbPrint = self.toolbar.AddLabelTool(
                wx.ID_ANY, 'Print Prescription',  BitmapFromBase64(toolbar_print_b64))
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

        #Prescription List

        self.prescriptionList = ObjectListViewCheck(self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.prescriptionList.SetColumns([
            ColumnDefn("Drug", "left", 180, "drug_name"),
            ColumnDefn("Order", "left", 140, "drug_order")])
        self.prescriptionList.SetEmptyListMsg("")
        self.prescriptionList.useAlternateBackColors = False
        self.prescriptionList.CreateCheckStateColumn()
        self.prescriptionList.Bind(EVT_OVL_CHECK_EVENT, self.OnRxCheck)
        self.prescriptionList.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnRxContextMenu)

        """
        self.prescriptionList = wx.CheckListBox(self)
        self.prescriptionList.Bind(wx.EVT_CHECKLISTBOX, self.OnRxCheck)
        self.prescriptionList.Bind(wx.EVT_CONTEXT_MENU, self.OnRxContextMenu)
        #self.prescriptionList.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRxContextMenu)
        """
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

        #id = 501
        #self.rxMenu.Append(id, "Remove All", "Remove All Medications.")
        #wx.EVT_MENU(self, id,  self.OnRemoveAllRx)

        self.unSet()


    def set(self, patient, listIndex):
        self.patient = patient
        self.listIndex = listIndex

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
        self.listIndex = None

        self.txtHospitalNo.ChangeValue("")
        self.txtNationalIdNo.ChangeValue("")
        self.txtBed.ChangeValue("")
        self.txtName.ChangeValue("")
        self.txtAge.ChangeValue("")
        self.txtSex.ChangeValue("")
        self.txtDiagnosis.ChangeValue("")

        self.prescriptionList.DeleteAllItems()
        #self.rxs = []

        self.Disable()
        

    def updateRx(self):
        self.prescriptionList.DeleteAllItems()
        self.rxs = []
        #index = 0
        for row in self.patient.rxs:
            #grid_row = self.prescriptionList.AppendRow()
            #self.prescriptionList.SetRow(grid_row, [bool(row.active), row.drug_name, row.drug_order ])
            #self.prescriptionList.Insert("{0} {1}".format(row.drug_name, row.drug_order), index)
            self.prescriptionList.AddObject(row)
            if row.active:
                self.prescriptionList.SetCheckState(row, True)
            else:
                self.prescriptionList.SetCheckState(row, False)
            #modelObject = self.prescriptionList.GetObjectAt(index)
            #if row.active:
            #    self.prescriptionList.SetCheckState(row, False)
            #else:
            #    self.prescriptionList.SetCheckState(row, True)
            #if row.active:
            #    self.prescriptionList.Check(index)
            #else:
            #    self.prescriptionList.Check(index, False)
            #self.rxs.append(row)
            #index += 1

        self.prescriptionList.RefreshObjects(self.prescriptionList.GetObjects())


        #objects = self.prescriptionList.GetObjects():

        #for obj in objects:
        #    self.prescriptionList.SetCheckState(obj, True)

        #self.Layout()


    def addDrug(self, drug_name, drug_order):
        drug = Rx(patient_id = self.patient.id, active = True, drug_name = drug_name, drug_order=drug_order)
        self.session.add(drug)
        self.session.commit()
        self.session.refresh(self.patient)
        self.updateRx()


    def OnChange(self, event):
        self.patient.hospital_no = str(self.txtHospitalNo.GetValue())
        self.patient.national_id_no = str(self.txtNationalIdNo.GetValue())
        self.patient.bed_no = str(self.txtBed.GetValue())
        self.patient.name = str(self.txtName.GetValue())
        self.patient.age = str(self.txtAge.GetValue())
        self.patient.sex = str(self.txtSex.GetValue())
        self.patient.diagnosis = str(self.txtDiagnosis.GetValue())

        self.patientListPanel.patientList.SetStringItem(self.listIndex, 0, str(self.patient.bed_no))
        self.patientListPanel.patientList.SetStringItem(self.listIndex, 1, str(self.patient.hospital_no))
        self.patientListPanel.patientList.SetStringItem(self.listIndex, 2, str(self.patient.name))

        self.session.commit()


    def OntxtBedKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txtHospitalNo.SetFocus()
            

    def OntxtHospitalNoKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txtNationalIdNo.SetFocus()

    
    def OntxtNationalIdNoKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txtName.SetFocus()

    
    def OntxtNameKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txtAge.SetFocus()

    
    def OntxtAgeKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txtSex.SetFocus()

    
    def OntxtSexKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txtDiagnosis.SetFocus()

   
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

    """
    def OnRemoveAllRx(self, event):
        dlg = wx.MessageDialog(None, 'Remove all medications?', 'Question', 
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        result = dlg.ShowModal()

        if (result != wx.ID_YES):
            return

        for rx in self.prescriptionList.GetObjects():
            self.session.delete(rx)

        self.session.commit()

        self.updateRx()
    """
    

    def OnPrint(self, event):
        if self.patient == None:
            return
        
        self.session.refresh(self.patient)

        c = canvas.Canvas("print.pdf", pagesize=A5)

        GeneratePrescription(self.patient, c)
        
        c.save()

        pdfV = PDFViewer(None)
        pdfV.viewer.UsePrintDirect = ``False``
        pdfV.viewer.LoadFile("print.pdf")
        pdfV.Show()
