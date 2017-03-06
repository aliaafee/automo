"""
Patients list panel
"""
import tempfile
import wx
from ObjectListView import ColumnDefn

from objectlistviewmod import ObjectListViewMod, EVT_OVL_CHECK_EVENT
from database import Patient
from pdfviewer import PDFViewer
from printing import generate_all_prescriptions,\
                     generate_patient_list,\
                     generate_patient_census_list
from images import bitmap_from_base64,\
                    toolbar_add_b64,\
                    toolbar_remove_b64,\
                    toolbar_print_census_b64,\
                    toolbar_print_list_b64,\
                    toolbar_print_all_b64


class PatientListPanel(wx.Panel):
    """
    Patients list panel
    """
    def __init__(self, parent, session, **kwds):
        super(PatientListPanel, self).__init__(parent, **kwds)

        self.session = session

        self.patient_panel = None
        self.selected_patient = None

        sizer = wx.BoxSizer(wx.VERTICAL)

        toolbar = wx.ToolBar(self, style=wx.TB_NODIVIDER)

        tb_add_patient = toolbar.AddLabelTool(
            wx.ID_ANY, 'Add', bitmap_from_base64(toolbar_add_b64), shortHelp="Add Patient")
        self.Bind(wx.EVT_TOOL, self.OnAddPatient, tb_add_patient)

        tb_remove_patient = toolbar.AddLabelTool(
            wx.ID_ANY, 'Remove', bitmap_from_base64(toolbar_remove_b64), shortHelp="Remove Selected Patients")
        self.Bind(wx.EVT_TOOL, self.OnRemovePatient, tb_remove_patient)

        tb_print_census_list = toolbar.AddLabelTool(
            wx.ID_ANY, 'Census', bitmap_from_base64(toolbar_print_census_b64), shortHelp="Print Census List")
        self.Bind(wx.EVT_TOOL, self.OnPrintCensusList, tb_print_census_list)

        tb_print_list = toolbar.AddLabelTool(
            wx.ID_ANY, 'List', bitmap_from_base64(toolbar_print_list_b64), shortHelp="Print Prescriptions List")
        self.Bind(wx.EVT_TOOL, self.OnPrintList, tb_print_list)

        tb_print_all = toolbar.AddLabelTool(
            wx.ID_ANY, 'All', bitmap_from_base64(toolbar_print_all_b64), shortHelp="Print All Prescriptions")
        self.Bind(wx.EVT_TOOL, self.OnPrintAll, tb_print_all)

        toolbar.Realize()

        sizer.Add(toolbar, 0, wx.ALL | wx. EXPAND)

        self.patient_list = ObjectListViewMod(self, style=wx.LC_REPORT)

        self.patient_list.SetColumns([
            #ColumnDefn("Bed", "left", 70, "bed_no", imageGetter=userImage),
            ColumnDefn("Bed", "left", 70, "bed_no"),
            ColumnDefn("Hospital No", "left", 70, "hospital_no"),
            ColumnDefn("Name", "left", 140, "name")
        ])

        self.patient_list.SetEmptyListMsg("")
        self.patient_list.useAlternateBackColors = False
        self.patient_list.CreateCheckStateColumn()

        self.patient_list.Bind(EVT_OVL_CHECK_EVENT, self.OnPatientCheck)
        self.patient_list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnPatientContextMenu)
        self.patient_list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnPatientSelected)

        sizer.Add(self.patient_list, 1, wx.ALL | wx. EXPAND, border=10)

        self.SetSizer(sizer)

        self.patient_menu = wx.Menu()
        menu_id = 600
        self.patient_menu.Append(menu_id, "Remove", "Remove Patient")
        wx.EVT_MENU(self, menu_id, self.OnRemovePatient)
        menu_id = 601
        self.patient_menu.Append(menu_id, "Tick All", "Tick All Patients")
        wx.EVT_MENU(self, menu_id, self.OnTickAllPatients)
        menu_id = 602
        self.patient_menu.Append(menu_id, "Untick All", "Untick All Patients")
        wx.EVT_MENU(self, menu_id, self.OnUntickAllPatients)


    def OnAddPatient(self, event):
        """ Add new patient """
        new_pt = Patient(
            active=True,
            bed_no="",
            hospital_no="",
            national_id_no="",
            name="",
            age="",
            sex="",
            diagnosis=""
        )

        self.session.add(new_pt)
        self.session.commit()

        self.UpdateList()

        self.selected_patient = new_pt

        self.patient_panel.set(self.selected_patient)
        self.patient_list.SelectObject(self.selected_patient)

        self.patient_panel.txt_bed.SetFocus()
        self.patient_panel.txt_bed.SetSelection(-1, -1)


    def OnRemovePatient(self, event):
        """ Remove selected patients """
        selected_patients = self.patient_list.GetSelectedObjects()

        if len(selected_patients) < 1:
            return

        dlg = wx.MessageDialog(None, 'Remove selected patients?', 'Remove Patient',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        result = dlg.ShowModal()

        if result != wx.ID_YES:
            return

        self.patient_panel.unset()

        for patient in selected_patients:
            self.session.delete(patient)

        self.session.commit()

        self.UpdateList()


    def OnPatientCheck(self, event):
        """ Save Tick patient """
        if event.value == True:
            event.object.active = True
        else:
            event.object.active = False
        self.session.commit()


    def OnPatientContextMenu(self, event):
        """ Show the context menu """
        self.PopupMenu(self.patient_menu)


    def OnTickAllPatients(self, event):
        """ Tick all patients """
        patients = self.patient_list.GetObjects()
        for patient in patients:
            patient.active = True
            self.patient_list.SetCheckState(patient, True)

        self.session.commit()
        self.patient_list.RefreshObjects(patients)


    def OnUntickAllPatients(self, event):
        """ Untick All Patients """
        patients = self.patient_list.GetObjects()
        for patient in patients:
            patient.active = False
            self.patient_list.SetCheckState(patient, False)

        self.session.commit()
        self.patient_list.RefreshObjects(patients)


    def _active_patient_count(self):
        return self.session.query(Patient).\
                            filter(Patient.active == True).\
                            count()


    def OnPrintAll(self, event):
        """ Print all active prescriptions """
        if self._active_patient_count == 0:
            dlg = wx.MessageDialog(None, 'Nothing to print. Add or tick patients.', 'Print All Prescriptions',
                                   wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            return

        temp_file = tempfile.mktemp(".pdf")

        generate_all_prescriptions(self.session, temp_file)

        pdf_view = PDFViewer(None, title="Print Preview")
        pdf_view.viewer.UsePrintDirect = ``False``
        pdf_view.viewer.LoadFile(temp_file)
        pdf_view.Show()


    def OnPrintList(self, event):
        """ Print prescriptions list"""
        if self._active_patient_count == 0:
            dlg = wx.MessageDialog(None, 'Nothing to print. Add or tick patients.', 'Print Prescription List',
                                   wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            return

        temp_file = tempfile.mktemp(".pdf")

        generate_patient_list(self.session, temp_file)

        pdf_view = PDFViewer(None, title="Print Preview")
        pdf_view.viewer.UsePrintDirect = ``False``
        pdf_view.viewer.LoadFile(temp_file)
        pdf_view.Show()


    def OnPrintCensusList(self, event):
        """ Print census list """
        if self._active_patient_count == 0:
            dlg = wx.MessageDialog(None, 'Nothing to print. Add or tick patients.', 'Print Census List',
                                   wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            return

        temp_file = tempfile.mktemp(".pdf")

        generate_patient_census_list(self.session, temp_file)

        pdf_view = PDFViewer(None, title="Print Preview")
        pdf_view.viewer.UsePrintDirect = ``False``
        pdf_view.viewer.LoadFile(temp_file)
        pdf_view.Show()



    def OnPatientSelected(self, event):
        """ Display the selected patient in the patient panel """
        list_selected = self.patient_list.GetSelectedObject()

        if list_selected is None:
            self.selected_patient = None
            self.patient_panel.unset()
            return

        self.selected_patient = list_selected

        self.patient_panel.set(self.selected_patient)


    def UpdateList(self):
        """ Update the patient list """
        self.patient_list.DeleteAllItems()

        for patient in self.session.query(Patient).order_by(Patient.bed_no):
            self.patient_list.AddObject(patient)
            if patient.active:
                self.patient_list.SetCheckState(patient, True)
            else:
                self.patient_list.SetCheckState(patient, False)

        self.patient_list.RefreshObjects(self.patient_list.GetObjects())

