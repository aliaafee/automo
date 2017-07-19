"""
Patient panel
"""
import wx

from patientinfo import PatientInfoPanelSmall
from dbqueryresultbox import DbQueryResultBox

from database import Admission
from database import format_duration
from admissionpanel import AdmissionPanel


class PatientPanel(wx.Panel):
    """
    Patient Panel
    """
    def __init__(self, parent, session, **kwds):
        super(PatientPanel, self).__init__(parent, **kwds)

        self.session = session
        self.patient = None

        sizer = wx.BoxSizer()

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self.right_panel = wx.Panel(splitter)
        right_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.patient_info = PatientInfoPanelSmall(self.right_panel, session)
        right_panel_sizer.Add(self.patient_info, 0, wx.ALL | wx.EXPAND, border=5)

        self.lbl_admissions = wx.StaticText(self.right_panel, label="Admissions")
        right_panel_sizer.Add(self.lbl_admissions, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)

        self.admissions_list = DbQueryResultBox(self.right_panel, self._admissions_decorator)
        self.admissions_list.Bind(wx.EVT_LISTBOX, self._on_admission_selected)
        right_panel_sizer.Add(self.admissions_list, 1, wx.EXPAND | wx.ALL, border=5)
        self.right_panel.SetSizer(right_panel_sizer)

        self.admission_panel = AdmissionPanel(splitter, self.session)

        splitter.SplitVertically(self.right_panel, self.admission_panel)
        splitter.SetMinimumPaneSize(100)
        splitter.SetSashPosition(250)
        sizer.Add(splitter, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.patient_info.Hide()
        self.lbl_admissions.Hide()
        self.admissions_list.Hide()



    def _admissions_decorator(self, admission_object, query_string):
        date_str = ""
        if admission_object.discharged_date is not None:
            date_str += "{0} ({1})".format(
                admission_object.admitted_date,
                format_duration(admission_object.admitted_date,
                                admission_object.discharged_date)
            )
        else:
            date_str += "{0} (current)".format(admission_object.admitted_date)

        diagnoses = []
        for condition in admission_object.conditions:
            diagnoses.append(condition.icd10class.preferred)
        diagnoses_str = "</li><li>".join(diagnoses)

        html = u'<table width="100%">'\
                    '<tr>'\
                        '<td><b>{0}</b></td>'\
                    '</tr>'\
                    '<tr>'\
                        '<td><ul><li>{1}</li></ul></td>'\
                    '</tr>'\
                '</table>'

        return html.format(date_str, diagnoses_str)


    def _on_admission_selected(self, event):
        if self.admission_panel.is_unsaved():
            self.admission_panel.save_changes()
            print "Changes saved"

        admission_selected = self.admissions_list.get_selected_object()

        if admission_selected is None:
            self.admission_panel.unset()
            return

        self.admission_panel.set(admission_selected)


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing"""
        if self.patient is None:
            return False

        if self.patient_info.is_unsaved():
            return True

        if self.admission_panel.is_unsaved():
            return True

        return False


    def unset(self, patient):
        self.patient = patient

        self.patient_info.clear()

        self.admissions_list.clear()

        self.admission_panel.unset()

        self.patient_info.Hide()
        self.lbl_admissions.Hide()
        self.admissions_list.Hide()
        self.right_panel.Layout()


    def set(self, patient):
        self.patient = patient

        self.patient_info.set(self.patient)

        admissions = self.session.query(Admission)\
                        .filter(Admission.patient_id == self.patient.id)\
                        .order_by(Admission.discharged_date)

        self.admissions_list.set_result(admissions)

        admissions_count = self.admissions_list.GetItemCount()
        if admissions_count > 0:
            self.admissions_list.SetSelection(0)
            self._on_admission_selected(None)
        else:
            self.admission_panel.unset()

        self.patient_info.Show()
        self.lbl_admissions.Show()
        self.admissions_list.Show()
        self.right_panel.Layout()
 

def main():
    #Testing
    import database
    database.StartEngine("sqlite:///wardpresc-data.db", False, "")
    session = database.Session()
    app = wx.PySimpleApp(0)

    mainFrame = wx.Frame(None, size=(800, 600))

    pnl = PatientPanel(mainFrame, session)

    patient = session.query(database.Patient)\
                .filter(database.Patient.id == 1)\
                .one()

    pnl.set(patient)

    app.SetTopWindow(mainFrame)

    mainFrame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()