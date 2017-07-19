"""Patient Information Panel. Minimal one and a detailed one"""
import wx
import datetime

from dbtextctrl import DbTextCtrl


class PatientInfoPanelSmall(wx.Panel):
    """Patient Panel Small, this is read-only"""
    def __init__(self, parent, session, **kwds):
        super(PatientInfoPanelSmall, self).__init__(parent, **kwds)

        self.session = session
        self.patient = None

        grid_sizer = wx.FlexGridSizer(5, 2, 2, 2)
        grid_sizer.AddGrowableCol(1, 1)

        label_width = 50

        self.lbl_hospital_no = wx.StaticText(self, label='Hosp No',
                                             size=wx.Size(label_width, -1))
        self.txt_hospital_no = DbTextCtrl(self, self.session)
        grid_sizer.Add(self.lbl_hospital_no, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_hospital_no, 1, wx.EXPAND)

        self.lbl_national_id_no = wx.StaticText(self, label='ID No',
                                                size=wx.Size(label_width, -1))
        self.txt_national_id_no = DbTextCtrl(self, self.session)
        grid_sizer.Add(self.lbl_national_id_no, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_national_id_no, 1, wx.EXPAND)

        self.lbl_name = wx.StaticText(self, label='Name', size=wx.Size(label_width, -1))
        self.txt_name = DbTextCtrl(self, self.session)
        grid_sizer.Add(self.lbl_name, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_name, 1, wx.EXPAND)

        self.lbl_age = wx.StaticText(self, label='Age', size=wx.Size(label_width, -1))
        self.txt_age = wx.TextCtrl(self)
        grid_sizer.Add(self.lbl_age, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_age, 1, wx.EXPAND)

        self.lbl_sex = wx.StaticText(self, label='Sex', size=wx.Size(label_width, -1))
        self.txt_sex = DbTextCtrl(self, self.session)
        grid_sizer.Add(self.lbl_sex, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_sex, 1, wx.EXPAND)

        self.txt_hospital_no.SetEditable(False)
        self.txt_national_id_no.SetEditable(False)
        self.txt_name.SetEditable(False)
        self.txt_age.SetEditable(False)
        self.txt_sex.SetEditable(False)

        self.SetSizer(grid_sizer)


    def set(self, patient):
        self.patient = patient

        self.txt_hospital_no.set_dbobject_attr(patient, "hospital_no")
        self.txt_national_id_no.set_dbobject_attr(patient, "national_id_no")
        self.txt_name.set_dbobject_attr(patient, "name")
        self.txt_sex.set_dbobject_attr(patient, "sex")

        self.txt_age.ChangeValue(patient.age())


    def clear(self):
        self.patient = None

        self.txt_hospital_no.set_dbobject_attr(None, "")
        self.txt_national_id_no.set_dbobject_attr(None, "")
        self.txt_name.set_dbobject_attr(None, "")
        self.txt_sex.set_dbobject_attr(None, "")

        self.txt_age.ChangeValue("")


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing
          always false in this panel as it is read-only"""
        return False


def main():
    import database
    database.StartEngine("sqlite:///wardpresc-data.db", False, "")
    session = database. Session()
    app = wx.PySimpleApp(0)

    mainFrame = wx.Frame(None)

    pnl = PatientInfoPanelSmall(mainFrame, session)

    patient = session.query(database.Patient)\
                .filter(database.Patient.id == 1)\
                .one()

    pnl.set(patient)

    app.SetTopWindow(mainFrame)

    mainFrame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()