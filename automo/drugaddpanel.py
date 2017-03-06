"""
Drug Add Panel, has a search box to selecte recently prescribed medications
and a text control to enter the drug order
"""
import wx

from actextcontroldb import ACTextControlDB
from database import Rx, Drug


class DrugAddPanel(wx.Panel):
    """
    Drug Add Panel, has a search box to selecte recently prescribed medications
    and a text control to enter the drug order
    """
    def __init__(self, parent, session, patient_panel, **kwds):
        super(DrugAddPanel, self).__init__(parent, **kwds)

        self.session = session
        self.patient_panel = patient_panel

        top_sizer = wx.BoxSizer(wx.VERTICAL)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.lbl_drug_name = wx.StaticText(self, label="Medication", size=wx.Size(-1, -1))
        sizer.Add(self.lbl_drug_name, 1, wx.RIGHT | wx.TOP | wx.EXPAND, border=5)

        self.lbl_drug_order = wx.StaticText(self, label="Order", size=wx.Size(-1, -1))
        sizer.Add(self.lbl_drug_order, 1, wx.RIGHT | wx.TOP | wx.EXPAND, border=5)

        self.lbl_add = wx.StaticText(self, label=" ", size=wx.Size(50, -1))
        sizer.Add(self.lbl_add, 0, wx.TOP, border=5)

        top_sizer.Add(sizer, 1, wx.EXPAND)

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.txt_drug_name = ACTextControlDB(self, self.session, Drug)
        self.txt_drug_name.Bind(wx.EVT_KEY_UP, self.OnDrugNameKeyUp)
        sizer.Add(self.txt_drug_name, 1, wx.RIGHT | wx.BOTTOM | wx.EXPAND, border=5)

        self.txt_drug_order = wx.TextCtrl(self, size=wx.Size(-1, -1))
        self.txt_drug_order.Bind(wx.EVT_KEY_UP, self.OnDrugOrderKeyUp)
        sizer.Add(self.txt_drug_order, 1, wx.RIGHT | wx.BOTTOM | wx.EXPAND, border=5)

        self.btn_add = wx.Button(self, label="Add", size=wx.Size(50, -1))
        self.btn_add.Bind(wx.EVT_BUTTON, self.OnAddDrug)
        sizer.Add(self.btn_add, 0, wx.BOTTOM, border=5)

        top_sizer.Add(sizer, 1, wx.EXPAND)

        self.SetSizer(top_sizer)

        self.update_drug_list()


    def OnDrugNameKeyUp(self, event):
        """Move to next text box when enter pressed"""
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txt_drug_order.SetFocus()


    def OnDrugOrderKeyUp(self, event):
        """Move to next text box when enter pressed"""
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.OnAddDrug(event)


    def update_drug_list(self):
        """Update drug list"""
        drugs = []

        for drug in self.session.query(Drug).order_by(Drug.name):
            drugs.append(drug.name)

        self.txt_drug_name.SetCandidates(drugs)


    def OnAddDrug(self, event):
        """Add new drug"""
        drug_name = self.txt_drug_name.GetValue()
        drug_order = self.txt_drug_order.GetValue()

        if drug_name == "":
            self.txt_drug_name.SetFocus()
            self.txt_drug_name.SetSelection(-1, -1)
            return

        new_presc = Rx(patient_id=self.patient_panel.patient.id,
                       drug_name=drug_name,
                       drug_order=drug_order,
                       active=True)

        self.session.add(new_presc)
        self.session.commit()

        self.txt_drug_name.ChangeValue("")
        self.txt_drug_order.ChangeValue("")

        self.patient_panel.update_rx()

        self.txt_drug_name.SetFocus()
