"""
Patient panel
"""
#import tempfile
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

        right_panel = wx.Panel(splitter)
        right_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.patient_info = PatientInfoPanelSmall(right_panel, session)
        right_panel_sizer.Add(self.patient_info, 0, wx.ALL | wx.EXPAND, border=5)

        lbl_admissions = wx.StaticText(right_panel, label="Admissions")
        right_panel_sizer.Add(lbl_admissions, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)

        self.admissions_list = DbQueryResultBox(right_panel, self.session,
                                               self._admissions_decorator)
        self.admissions_list.Bind(wx.EVT_LISTBOX, self._on_admission_selected)
        right_panel_sizer.Add(self.admissions_list, 1, wx.EXPAND | wx.ALL, border=5)
        right_panel.SetSizer(right_panel_sizer)

        self.admission_panel = AdmissionPanel(splitter, self.session)

        splitter.SplitVertically(right_panel, self.admission_panel)
        splitter.SetSashPosition(250)
        sizer.Add(splitter, 1, wx.EXPAND)

        self.SetSizer(sizer)


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
            return

        self.admission_panel.set(admission_selected)


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing"""
        if self.patient_info.is_unsaved():
            return True

        if self.admission_panel.is_unsaved():
            return True

        return False


    def set(self, patient):
        self.patient = patient

        self.patient_info.set(self.patient)

        admissions = self.session.query(Admission)\
                        .filter(Admission.patient_id == self.patient.id)\
                        .order_by(Admission.discharged_date)

        self.admissions_list.set_result(admissions)

def main():
    import database
    database.StartEngine("sqlite:///wardpresc-data.db", False, "")
    session = database. Session()
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


######TO DELETE############


class PatientPanelOld(wx.Panel):
    """
    Patient panel
    """
    def __init__(self, parent, session, **kwds):
        super(PatientPanelOld, self).__init__(parent, **kwds)

        self.session = session
        self.patient_list_panel = None

        self.patient = None

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = wx.ToolBar(self, style=wx.TB_NODIVIDER)

        self.tb_print = self.toolbar.AddLabelTool(
            wx.ID_ANY, 'Print', bitmap_from_base64(toolbar_print_one_b64),
            shortHelp="Print Prescription")
        self.Bind(wx.EVT_TOOL, self.OnPrint, self.tb_print)

        self.toolbar.AddStretchableSpace()

        self.lbl_doctor = wx.StaticText(self.toolbar, label="Doctor's Name  ", size=wx.Size(-1, -1))
        self.toolbar.AddControl(self.lbl_doctor)
        self.txt_doctor = AcDbTextCtrl(self.toolbar, self.session, Doctor)
        self.toolbar.AddControl(self.txt_doctor)

        self.toolbar.Realize()

        sizer.Add(self.toolbar, 0, wx.ALL | wx. EXPAND)

        grid_sizer = wx.FlexGridSizer(8, 2, 5, 5)
        grid_sizer.AddGrowableCol(1, 1)

        label_width = 100

        self.lbl_bed = wx.StaticText(self, label='Bed', size=wx.Size(label_width, -1))
        self.txt_bed = DbTextCtrl(self, self.session, self.OnChangeList)
        grid_sizer.Add(self.lbl_bed, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_bed, 1, wx.EXPAND)

        self.lbl_hospital_no = wx.StaticText(self, label='Hospital No',
                                             size=wx.Size(label_width, -1))
        self.txt_hospital_no = DbTextCtrl(self, self.session, self.OnChangeList)
        grid_sizer.Add(self.lbl_hospital_no, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_hospital_no, 1, wx.EXPAND)

        self.lbl_national_id_no = wx.StaticText(self, label='National Id No',
                                                size=wx.Size(label_width, -1))
        self.txt_national_id_no = DbTextCtrl(self, self.session)
        grid_sizer.Add(self.lbl_national_id_no, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_national_id_no, 1, wx.EXPAND)

        self.lbl_name = wx.StaticText(self, label='Name', size=wx.Size(label_width, -1))
        self.txt_name = DbTextCtrl(self, self.session, self.OnChangeList)
        grid_sizer.Add(self.lbl_name, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_name, 1, wx.EXPAND)

        self.lbl_age = wx.StaticText(self, label='Age', size=wx.Size(label_width, -1))
        self.txt_age = DbTextCtrl(self, self.session)
        grid_sizer.Add(self.lbl_age, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_age, 1, wx.EXPAND)

        self.lbl_sex = wx.StaticText(self, label='Sex', size=wx.Size(label_width, -1))
        self.txt_sex = DbTextCtrl(self, self.session)
        grid_sizer.Add(self.lbl_sex, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_sex, 1, wx.EXPAND)

        self.lbl_diagnosis = wx.StaticText(self, label='Diagnosis', size=wx.Size(label_width, -1))
        self.txt_diagnosis = AcDbTextCtrl(self, self.session, Diagnosis)
        grid_sizer.Add(self.lbl_diagnosis, 1, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL)
        grid_sizer.Add(self.txt_diagnosis, 1, wx.EXPAND)

        sizer.Add(grid_sizer, 0, wx.ALL | wx.EXPAND, border=10)

        self.txt_drug_name = DrugAddPanel(self, self.session, self)
        sizer.Add(self.txt_drug_name, 0, wx.RIGHT | wx.LEFT | wx.EXPAND, border=10)

        self.prescription_list = ObjectListViewMod(
            self,
            style=wx.LC_REPORT|wx.SUNKEN_BORDER,
            cellEditMode=ObjectListView.CELLEDIT_DOUBLECLICK
        )

        self.prescription_list.SetColumns([
            ColumnDefn("Drug", "left", 180, "drug", isEditable=False),
            ColumnDefn("Order", "left", 140, "drug_order")
        ])

        self.prescription_list.SetEmptyListMsg("")
        self.prescription_list.useAlternateBackColors = False
        self.prescription_list.CreateCheckStateColumn()

        self.prescription_list.Bind(EVT_OVL_CHECK_EVENT, self.OnRxCheck)
        self.prescription_list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnRxContextMenu)
        self.prescription_list.Bind(OLVEvent.EVT_CELL_EDIT_FINISHED, self.OnCellEditFinished)

        sizer.Add(self.prescription_list, 1, wx.RIGHT | wx.LEFT | wx.BOTTOM | wx. EXPAND, border=10)

        #Enter Treversal
        self.txt_bed.Bind(wx.EVT_KEY_UP, self.OntxtBedKeyUp)
        self.txt_hospital_no.Bind(wx.EVT_KEY_UP, self.OntxtHospitalNoKeyUp)
        self.txt_national_id_no.Bind(wx.EVT_KEY_UP, self.OntxtNationalIdNoKeyUp)
        self.txt_name.Bind(wx.EVT_KEY_UP, self.OntxtNameKeyUp)
        self.txt_age.Bind(wx.EVT_KEY_UP, self.OntxtAgeKeyUp)
        self.txt_sex.Bind(wx.EVT_KEY_UP, self.OntxtSexKeyUp)
        self.txt_diagnosis.Bind(wx.EVT_KEY_UP, self.OntxtDiagnosisKeyUp)

        self.SetSizer(sizer)

        self.rx_menu = wx.Menu()
        menu_id = 500
        self.rx_menu.Append(menu_id, "Remove", "Remove Medication.")
        wx.EVT_MENU(self, menu_id, self.OnRemoveRx)
        menu_id = 501
        self.rx_menu.Append(menu_id, "Tick All", "Tick All Medications")
        wx.EVT_MENU(self, menu_id, self.OnTickAllRx)
        menu_id = 502
        self.rx_menu.Append(menu_id, "Untick All", "Untick All Medications")
        wx.EVT_MENU(self, menu_id, self.OnUntickAllRx)

        self.unset()


    def set(self, patient):
        """ Set Patient """
        self.patient = patient

        self.txt_hospital_no.SetDbObjectAttr(patient, "hospital_no")
        self.txt_national_id_no.SetDbObjectAttr(patient, "national_id_no")
        self.txt_bed.SetDbObjectAttr(patient, "bed_no")
        self.txt_name.SetDbObjectAttr(patient, "name")
        self.txt_age.SetDbObjectAttr(patient, "age")
        self.txt_sex.SetDbObjectAttr(patient, "sex")

        self.txt_diagnosis.SetDbObjectAttr(patient, "diagnosis")#.ChangeValue(str(patient.diagnosis))

        self.update_rx()

        self.toolbar.EnableTool(self.tb_print.GetId(), True)
        self.txt_hospital_no.Enable()
        self.txt_national_id_no.Enable()
        self.txt_bed.Enable()
        self.txt_name.Enable()
        self.txt_age.Enable()
        self.txt_sex.Enable()
        self.txt_diagnosis.Enable()
        self.txt_drug_name.Enable()
        self.prescription_list.Enable()


    def unset(self):
        """ Clear the panel """
        self.patient = None

        self.txt_hospital_no.SetDbObjectAttr(None, "")
        self.txt_national_id_no.SetDbObjectAttr(None, "")
        self.txt_bed.SetDbObjectAttr(None, "")
        self.txt_name.SetDbObjectAttr(None, "")
        self.txt_age.SetDbObjectAttr(None, "")
        self.txt_sex.SetDbObjectAttr(None, "")

        self.txt_diagnosis.SetDbObjectAttr(None, "")#.ChangeValue("")

        self.prescription_list.DeleteAllItems()

        self.toolbar.EnableTool(self.tb_print.GetId(), False)
        self.txt_hospital_no.Disable()
        self.txt_national_id_no.Disable()
        self.txt_bed.Disable()
        self.txt_name.Disable()
        self.txt_age.Disable()
        self.txt_sex.Disable()
        self.txt_diagnosis.Disable()
        self.txt_drug_name.Disable()
        self.prescription_list.Disable()


    def update_rx(self):
        """ Update the medications list """
        self.prescription_list.DeleteAllItems()

        for row in self.patient.rxs:
            self.prescription_list.AddObject(row)
            if row.active:
                self.prescription_list.SetCheckState(row, True)
            else:
                self.prescription_list.SetCheckState(row, False)

        self.prescription_list.RefreshObjects(self.prescription_list.GetObjects())


    def OnChangeList(self, event):
        """ Update patient list to reflect changes """
        self.patient_list_panel.patient_list.RefreshObjects([self.patient])


    def OnCellEditFinished(self, event):
        """ Save changes to drug order in the drug list """
        self.session.commit()


    def OntxtBedKeyUp(self, event):
        """ Enter treversal """
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txt_hospital_no.SetFocus()
            self.txt_hospital_no.SetSelection(-1, -1)


    def OntxtHospitalNoKeyUp(self, event):
        """ Enter treversal """
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txt_national_id_no.SetFocus()
            self.txt_national_id_no.SetSelection(-1, -1)


    def OntxtNationalIdNoKeyUp(self, event):
        """ Enter treversal """
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txt_name.SetFocus()
            self.txt_name.SetSelection(-1, -1)


    def OntxtNameKeyUp(self, event):
        """ Enter treversal """
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txt_age.SetFocus()
            self.txt_age.SetSelection(-1, -1)


    def OntxtAgeKeyUp(self, event):
        """ Enter treversal """
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txt_sex.SetFocus()
            self.txt_sex.SetSelection(-1, -1)


    def OntxtSexKeyUp(self, event):
        """ Enter treversal """
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txt_diagnosis.SetFocus()
            self.txt_diagnosis.SetSelection(-1, -1)


    def OntxtDiagnosisKeyUp(self, event):
        """ Enter treversal """
        if event.GetKeyCode() == wx.WXK_RETURN:
            self.txt_drug_name.txt_drug_name.SetFocus()
            self.txt_drug_name.txt_drug_name.SetSelection(-1, -1)


    def OnRxCheck(self, event):
        """ Enter treversal """
        if event.value is True:
            event.object.active = True
        else:
            event.object.active = False
        self.session.commit()


    def OnRxContextMenu(self, event):
        """ Show medication list context menu """
        self.PopupMenu(self.rx_menu)


    def OnTickAllRx(self, event):
        """ Tick all medications """
        rxs = self.prescription_list.GetObjects()
        for rx in rxs:
            rx.active = True
            self.prescription_list.SetCheckState(rx, True)

        self.session.commit()
        self.prescription_list.RefreshObjects(rxs)


    def OnUntickAllRx(self, event):
        """ Untick all medications """
        rxs = self.prescription_list.GetObjects()
        for rx in rxs:
            rx.active = False
            self.prescription_list.SetCheckState(rx, False)

        self.session.commit()
        self.prescription_list.RefreshObjects(rxs)


    def OnRemoveRx(self, event):
        """ Remove medication """
        dlg = wx.MessageDialog(None, 'Remove selected medications?', 'Remove Medication',
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        result = dlg.ShowModal()

        if result != wx.ID_YES:
            return

        for rx in self.prescription_list.GetSelectedObjects():
            self.session.delete(rx)

        self.session.commit()

        self.update_rx()


    def OnPrint(self, event):
        """ Print this prescription """
        if self.patient is None:
            return

        self.session.refresh(self.patient)

        temp_file = tempfile.mktemp(".pdf")

        generate_prescription(self.session, self.patient, self.txt_doctor.GetValue(), temp_file)

        pdf_view = PDFViewer(None, title="Print Preview")
        pdf_view.viewer.UsePrintDirect = ``False``
        pdf_view.viewer.LoadFile(temp_file)
        pdf_view.Show()


