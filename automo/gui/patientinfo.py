"""Patient Information Panel. Minimal one and a detailed one"""
import wx

from .. import config
from .. import database as db


class PatientInfoPanelSmall(wx.Panel):
    """Patient Panel Small, this is read-only"""
    def __init__(self, parent, session, style=wx.BORDER_RAISED, **kwds):
        super(PatientInfoPanelSmall, self).__init__(parent, style=style, **kwds)

        self.session = session
        self.patient = None

        lbl_font = self.GetFont()
        bold_font = self.GetFont()
        bold_font.SetWeight(wx.BOLD)
        med_font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        big_font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        self.lbl_lbl_hospital_no = wx.StaticText(self, label='IP No', size=(40,-1))
        self.lbl_lbl_hospital_no.SetFont(lbl_font)

        self.lbl_hospital_no = wx.StaticText(self, label='', size=(60,-1))
        self.lbl_hospital_no.SetFont(bold_font)

        self.lbl_lbl_national_id_no = wx.StaticText(self, label='ID No', size=(40, -1))
        self.lbl_lbl_national_id_no.SetFont(lbl_font)

        self.lbl_national_id_no = wx.StaticText(self, label='', size=(60, -1))
        self.lbl_national_id_no.SetFont(bold_font)

        self.lbl_name = wx.StaticText(self, label='')
        self.lbl_name.SetFont(big_font)

        self.lbl_age_sex = wx.StaticText(self, label='')
        self.lbl_age_sex.SetFont(med_font)

        self.lbl_weight = wx.StaticText(self, label="", size=(60,-1))
        self.lbl_height = wx.StaticText(self, label="", size=(60,-1))
        self.lbl_bmi = wx.StaticText(self, label="", size=(60,-1))
        
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
        hsizer.Add(self.lbl_age_sex, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
        hsizer.Add(msizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)

        self.SetSizer(hsizer)


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
