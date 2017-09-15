"""Patient Information Panel. Minimal one and a detailed one"""
import wx

from .. import config
from .. import database as db
from . import images
from .pydatepickerctrl import PyDatePickerCtrl
from .dbaddressctrl import DbAddressCtrl
from .basedialog import BaseDialog


class PatientInfoPanelSmall(wx.Panel):
    """Patient Panel Small, this is read-only"""
    def __init__(self, parent, session, style=wx.BORDER_RAISED, **kwds):
        super(PatientInfoPanelSmall, self).__init__(parent, style=style, **kwds)

        self.session = session
        self.patient = None

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)
        self.toolbar.AddLabelTool(wx.ID_EDIT, "Edit", images.get("edit_24"), wx.NullBitmap, wx.ITEM_NORMAL, "Edit Patient", "")
        self.toolbar.AddStretchableSpace()
        self.toolbar.Realize()

        lbl_font = self.GetFont()
        bold_font = self.GetFont()
        bold_font.SetWeight(wx.BOLD)
        med_font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        big_font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        self.lbl_lbl_hospital_no = wx.StaticText(self, label='IP No', size=(40,-1))
        self.lbl_lbl_hospital_no.SetFont(lbl_font)

        self.lbl_hospital_no = wx.StaticText(self, label='', size=(-1,-1))
        self.lbl_hospital_no.SetFont(bold_font)

        self.lbl_lbl_national_id_no = wx.StaticText(self, label='ID No', size=(40, -1))
        self.lbl_lbl_national_id_no.SetFont(lbl_font)

        self.lbl_national_id_no = wx.StaticText(self, label='', size=(-1, -1))
        self.lbl_national_id_no.SetFont(bold_font)

        self.lbl_name = wx.StaticText(self, label='')
        self.lbl_name.SetFont(big_font)

        self.lbl_age_sex = wx.StaticText(self, label='')
        self.lbl_age_sex.SetFont(med_font)

        self.lbl_weight = wx.StaticText(self, label="")
        self.lbl_height = wx.StaticText(self, label="")
        self.lbl_bmi = wx.StaticText(self, label="")
        
        grid_sizer = wx.FlexGridSizer(2, 2, 2, 2)
        grid_sizer.Add(self.lbl_lbl_hospital_no, 1, wx.EXPAND)
        grid_sizer.Add(self.lbl_hospital_no, 1, wx.EXPAND)
        grid_sizer.Add(self.lbl_lbl_national_id_no, 1, wx.EXPAND)
        grid_sizer.Add(self.lbl_national_id_no, 1, wx.EXPAND)
        msizer = wx.BoxSizer(wx.VERTICAL)
        msizer.Add(self.lbl_weight, 0, wx.EXPAND)
        msizer.Add(self.lbl_height, 0, wx.EXPAND)
        msizer.Add(self.lbl_bmi, 0, wx.EXPAND)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(grid_sizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hsizer.Add(self.lbl_name, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hsizer.Add(self.lbl_age_sex, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hsizer.Add(msizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        #hsizer.AddStretchSpacer()
        hsizer.Add(self.toolbar, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)

        self.SetSizer(hsizer)


    def refresh(self):
        """Refresh the panel"""
        self.set(self.patient)
        self.Layout()


    def set(self, patient):
        """Set selected patient"""
        if patient is None:
            self.unset()
            return

        self.patient = patient

        age = self.patient.age
        if age is None:
            if self.patient.time_of_death is not None:
                age_str = "(<i>Deceased</i> on {})".format(config.format_date(self.patient.time_of_death))
            else:
                age_str = "?"
        else:
            age_str = config.format_duration(age)


        self.lbl_hospital_no.SetLabelMarkup("<b>{}</b>".format(self.patient.hospital_no))
        self.lbl_national_id_no.SetLabelMarkup("<b>{}</b>".format(self.patient.national_id_no))
        self.lbl_name.SetLabelMarkup("<b>{}</b>".format(self.patient.name))
        self.lbl_age_sex.SetLabelMarkup("<b>{0} / {1}</b>".format(age_str, self.patient.sex))
        
        measurements = self.session.query(db.Measurements)\
                            .filter(db.Measurements.patient == self.patient)\
                            .order_by(db.Measurements.start_time.desc())\
                            .limit(1)
        if measurements.count() == 1:
            measurement = measurements.one()
            if measurement.weight is not None:
                self.lbl_weight.SetLabel("Wt {}kg".format(round(measurement.weight,1)))
            else:
                self.lbl_weight.SetLabel("")
            if measurement.height is not None:
                self.lbl_height.SetLabel("Ht {}m".format(round(measurement.height,2)))
            else:
                self.lbl_height.SetLabel("")
            if measurement.bmi is not None:
                self.lbl_bmi.SetLabel("BMI {}".format(round(measurement.bmi,2)))
            else:
                self.lbl_bmi.SetLabel("")
        else:
            self.lbl_weight.SetLabel("")
            self.lbl_height.SetLabel("")
            self.lbl_bmi.SetLabel("")

    def unset(self):
        """Clear selected patient"""
        self.patient = None

        self.lbl_hospital_no.SetLabel("")
        self.lbl_national_id_no.SetLabel("")
        self.lbl_name.SetLabel("")
        self.lbl_age_sex.SetLabel("")
        self.lbl_weight.SetLabel("")
        self.lbl_height.SetLabel("")
        self.lbl_bmi.SetLabel("")


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing
          always false in this panel as it is read-only"""
        return False




class PatientInfoEditorPanel(wx.ScrolledWindow):
    """Panel to edit patient information"""
    def __init__(self, parent, style=wx.VSCROLL, **kwds):
        super(PatientInfoEditorPanel, self).__init__(parent, style=style, **kwds)

        self.txt_hospital_no = wx.TextCtrl(self)
        self.txt_national_id_no = wx.TextCtrl(self)
        self.txt_name = wx.TextCtrl(self)
        self.txt_time_of_birth = PyDatePickerCtrl(self, style=wx.DP_DROPDOWN)
        self.txt_phone_no = wx.TextCtrl(self)
        self.txt_sex = wx.TextCtrl(self)
        self.txt_permanent_address = DbAddressCtrl(self) #wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.txt_current_address = DbAddressCtrl(self) #wx.TextCtrl(self, style=wx.TE_MULTILINE)

        grid_sizer = wx.FlexGridSizer(8, 2, 5, 5)
        grid_sizer.AddMany([
            (wx.StaticText(self, label="Hospital No."), 1, wx.EXPAND),
            (self.txt_hospital_no, 1, wx.EXPAND),
            (wx.StaticText(self, label="National ID No."), 1, wx.EXPAND),
            (self.txt_national_id_no, 1, wx.EXPAND),
            (wx.StaticText(self, label="Name"), 1, wx.EXPAND),
            (self.txt_name, 1, wx.EXPAND),
            (wx.StaticText(self, label="Date of Birth"), 1, wx.EXPAND),
            (self.txt_time_of_birth, 1, wx.EXPAND),
            (wx.StaticText(self, label="Sex"), 1, wx.EXPAND),
            (self.txt_sex, 1, wx.EXPAND),
            (wx.StaticText(self, label="Phone No."), 1, wx.EXPAND),
            (self.txt_phone_no, 1, wx.EXPAND),
            (wx.StaticText(self, label="Permanent Address"), 1, wx.EXPAND),
            (self.txt_permanent_address, 1, wx.EXPAND),
            (wx.StaticText(self, label="Current Address"), 1, wx.EXPAND),
            (self.txt_current_address, 1, wx.EXPAND),
        ])
        grid_sizer.AddGrowableCol(1)

        self.SetSizer(grid_sizer)

        self.SetScrollbars(20,20,55,40)


    def set(self, patient):
        """Set patient data"""
        self.txt_hospital_no.SetValue(patient.hospital_no)
        self.txt_national_id_no.SetValue(patient.national_id_no)
        self.txt_name.SetValue(patient.name)
        self.txt_time_of_birth.set_pydatetime(patient.time_of_birth)
        self.txt_phone_no.SetValue(patient.phone_no)
        self.txt_sex.SetValue(patient.sex)
        self.txt_permanent_address.set(patient.permanent_address)
        self.txt_current_address.set(patient.current_address)
        


    def get(self):
        """Get patient data as a patient object"""
        patient = db.Patient()
        patient.hospital_no = self.txt_hospital_no.GetValue()
        patient.national_id_no = self.txt_national_id_no.GetValue()
        patient.name = self.txt_name.GetValue()
        #if self.txt_age.GetValue() == "":
        patient.time_of_birth = self.txt_time_of_birth.get_pydatetime()
        #else:
        #    patient.age = config.parse_duration(self.txt_age.GetValue())
        patient.phone_no = self.txt_phone_no.GetValue()
        patient.sex = self.txt_sex.GetValue()
        patient.permanent_address = self.txt_permanent_address.get()
        patient.current_address = self.txt_current_address.get()
        return patient


class PatientInfoEditorDialog(BaseDialog):
    def __init__(self, parent, **kwds):
        super(PatientInfoEditorDialog, self).__init__(parent, **kwds)
        self.SetTitle("Patient")
        self.patient_info = PatientInfoEditorPanel(self)
        self.setup_sizers()


    def setup_contents(self):
        self.content_sizer.Add(self.patient_info, 1, wx.EXPAND | wx.ALL, border=5)


    def set(self, patient):
        self.patient_info.set(patient)


    def get(self):
        return self.patient_info.get()
