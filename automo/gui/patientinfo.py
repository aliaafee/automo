"""Patient Information Panel. Minimal one and a detailed one"""
import wx

from .. import config
from .. import database as db
from . import images
from .dbform import DbFormPanel,\
                    DbFormDialog,\
                    DbStringField,\
                    DbDateTimeField,\
                    DbAddressField,\
                    DbEnumField,\
                    DbOptionalMultilineStringField,\
                    DbDurationField


class PatientInfoPanelSmall(wx.Panel):
    """Patient Panel Small, this is read-only"""
    def __init__(self, parent, session, style=wx.BORDER_THEME, **kwds):
        super(PatientInfoPanelSmall, self).__init__(parent, style=style, **kwds)

        self.session = session
        self.patient = None

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)

        self.lbl_font = self.GetFont()
        self.alert_font = wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD)
        bold_font = self.GetFont()
        bold_font.SetWeight(wx.BOLD)
        med_font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        big_font = wx.Font(18, wx.DEFAULT, wx.NORMAL, wx.BOLD)

        self.lbl_lbl_hospital_no = wx.StaticText(self, label='IP No', size=(40,-1))
        self.lbl_lbl_hospital_no.SetFont(self.lbl_font)

        self.lbl_hospital_no = wx.StaticText(self, label='', size=(-1,-1))
        self.lbl_hospital_no.SetFont(bold_font)

        self.lbl_lbl_national_id_no = wx.StaticText(self, label='ID No', size=(40, -1))
        self.lbl_lbl_national_id_no.SetFont(self.lbl_font)

        self.lbl_national_id_no = wx.StaticText(self, label='', size=(-1, -1))
        self.lbl_national_id_no.SetFont(bold_font)

        self.lbl_name = wx.StaticText(self, label='')
        self.lbl_name.SetFont(big_font)

        self.lbl_age_sex = wx.StaticText(self, label='')
        self.lbl_age_sex.SetFont(med_font)

        self.lbl_weight = wx.StaticText(self, label="")
        self.lbl_height = wx.StaticText(self, label="")
        self.lbl_bmi = wx.StaticText(self, label="")

        self.lbl_allergies = wx.StaticText(self, label="")
        
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
        hsizer.Add(self.lbl_allergies, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, border=5)
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
        
        weight = None
        measurements = self.session.query(db.Measurements)\
                            .filter(db.Measurements.patient == self.patient)\
                            .filter(db.Measurements.weight != None)\
                            .order_by(db.Measurements.start_time.desc())\
                            .limit(1)
        if measurements.count() == 1:
            measurement = measurements.one()
            weight = measurement.weight
            self.lbl_weight.SetLabel("Wt {0} kg".format(round(weight,1)))
        else:
            self.lbl_weight.SetLabel("")

        height = None
        measurements = self.session.query(db.Measurements)\
                            .filter(db.Measurements.patient == self.patient)\
                            .filter(db.Measurements.height != None)\
                            .order_by(db.Measurements.start_time.desc())\
                            .limit(1)
        if measurements.count() == 1:
            measurement = measurements.one()
            height = measurement.height
            self.lbl_height.SetLabel("Ht {0} m".format(round(height,2)))
        else:
            self.lbl_height.SetLabel("")

        if weight is not None and height is not None:
            bmi = weight / (height ** 2)
            self.lbl_bmi.SetLabel(u"BMI {} kg/m\u00B2".format(round(bmi,2)))
        else:
            self.lbl_bmi.SetLabel("")

        """
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
            
        """

        if self.patient.allergies is None:
            self.lbl_allergies.SetLabel("No Known Allergies")
            self.lbl_allergies.SetFont(self.lbl_font)
            self.lbl_allergies.SetForegroundColour(wx.Colour(0,0,0))
        else:
            self.lbl_allergies.SetLabel("Allergic to: {}".format(self.patient.allergies))
            self.lbl_allergies.SetFont(self.alert_font)
            self.lbl_allergies.SetForegroundColour(wx.Colour(255,0,0))

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



class PatientForm(DbFormDialog):
    """Patient Data Form"""
    def __init__(self, parent, **kwds):
        fields = [
            DbStringField("Hospital No.", "hospital_no", required=True),
            DbStringField("National Id No.", "national_id_no", required=True),
            DbStringField("Name", "name", required=True),
            DbDateTimeField("Date of Birth", "time_of_birth", required=True),
            DbEnumField("Sex", "sex", ["M", "F"], required=True),
            DbOptionalMultilineStringField("Known Allergies", "allergies", lines=3),
            DbStringField("Phone No.", "phone_no"),
            DbAddressField("Current Address", "current_address"),
            DbAddressField("Permanent Address", "permanent_address")
        ]
        super(PatientForm, self).__init__(parent, db.Patient, fields, size=(500, 500), **kwds)



class PatientFormPanel(DbFormPanel):
    """Patient Data Form"""
    def __init__(self, parent, **kwds):
        fields = [
            DbStringField("Hospital No.", "hospital_no", required=True),
            DbStringField("National Id No.", "national_id_no", required=True),
            DbStringField("Name", "name", required=True),
            DbDurationField("Age (_y _m _d)", "age", required=True),
            DbEnumField("Sex", "sex", ["M", "F"], required=True),
            DbOptionalMultilineStringField("Known Allergies", "allergies", lines=3),
            DbStringField("Phone No.", "phone_no"),
            DbAddressField("Current Address", "current_address"),
            DbAddressField("Permanent Address", "permanent_address")
        ]
        super(PatientFormPanel, self).__init__(parent, db.Patient, fields, **kwds)
