import wx
import time

from actextcontroldb import ACTextControlDB
from database import Rx, Drug


class DrugAddPanel(wx.Panel):
    def __init__(self, parent, session, patientPanel, **kwds):
        super(DrugAddPanel, self).__init__(parent, **kwds)

        self.session = session
        self.patientPanel = patientPanel

        topSizer = wx.BoxSizer(wx.VERTICAL)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.lblDrugName = wx.StaticText(self, label="Medication", size=wx.Size(-1,-1))
        sizer.Add(self.lblDrugName, 1, wx.RIGHT | wx.TOP | wx.EXPAND, border=5)

        self.lblDrugOrder = wx.StaticText(self, label="Order", size=wx.Size(-1,-1))
        sizer.Add(self.lblDrugOrder, 1, wx.RIGHT | wx.TOP | wx.EXPAND, border=5)

        self.lblAdd = wx.StaticText(self, label=" ", size=wx.Size(50,-1))
        sizer.Add(self.lblAdd, 0, wx.TOP , border=5)

        topSizer.Add(sizer, 1, wx.EXPAND)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.txtDrugName = ACTextControlDB(self, self.session, Drug)
        self.txtDrugName.Bind(wx.EVT_KEY_UP, self.OnDrugNameKeyUp)
        sizer.Add(self.txtDrugName, 1, wx.RIGHT | wx.BOTTOM | wx.EXPAND, border=5)

        self.txtDrugOrder = wx.TextCtrl(self, size=wx.Size(-1,-1))
        self.txtDrugOrder.Bind(wx.EVT_KEY_UP, self.OnDrugOrderKeyUp)
        sizer.Add(self.txtDrugOrder, 1, wx.RIGHT | wx.BOTTOM | wx.EXPAND, border=5)

        self.btnAdd = wx.Button(self, label="Add", size=wx.Size(50,-1))
        self.btnAdd.Bind(wx.EVT_BUTTON, self.OnAddDrug)
        sizer.Add(self.btnAdd, 0, wx.BOTTOM, border=5)

        topSizer.Add(sizer, 1, wx.EXPAND)
        
        self.SetSizer(topSizer)

        self.UpdateDrugList()


    def OnDrugNameKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txtDrugOrder.SetFocus()


    def OnDrugOrderKeyUp(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.OnAddDrug(event)


    def UpdateDrugList(self):
        drugs = []
        
        for drug in self.session.query(Drug).order_by(Drug.name):
            drugs.append(drug.name)
            
        self.txtDrugName.SetCandidates(drugs)
            

    def OnAddDrug(self, event):
        drug_name = self.txtDrugName.GetValue()
        drug_order = self.txtDrugOrder.GetValue()

        if drug_name == "":        
            self.txtDrugName.SetFocus()
            self.txtDrugName.SetSelection(-1,-1)
            return

        #if drug_order == "":            
        #    self.txtDrugOrder.SetFocus()
        #    self.txtDrugOrder.SetSelection(-1,-1)
        #    return

        new_presc = Rx( patient_id = self.patientPanel.patient.id,
                        drug_name = drug_name,
                        drug_order = drug_order,
                        active = True)

        self.session.add(new_presc)
        self.session.commit() 

        self.txtDrugName.ChangeValue("")
        self.txtDrugOrder.ChangeValue("")
        
        self.patientPanel.updateRx()

        self.txtDrugName.SetFocus()
