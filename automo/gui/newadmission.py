import wx
import wx.wizard

from .. import database as db
from .dbcombobox import DbComboBox
from .patientinfo import PatientFormPanel
from .dbqueryresultbox import DbQueryResultBox
from .patientsearchpanel import PatientSearchPanel


class BasePage(wx.wizard.PyWizardPage):
    def __init__(self, parent, session, title):
        super(BasePage, self).__init__(parent)
        self.next = self.prev = None
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label=title)
        title.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.sizer.Add(title, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        self.SetSizer(self.sizer)
        self.session = session
        self.error_message = "Error"

    def is_valid(self):
        return True

    def show_error(self):
        with wx.MessageDialog(None,
                              self.error_message,
                              "Error",
                              wx.OK | wx.ICON_EXCLAMATION) as dlg:
            dlg.ShowModal()
            dlg.Destroy()

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next

    def GetPrev(self):
        return self.prev


class PatientSelectorPage(BasePage):
    def __init__(self, parent, session):
        super(PatientSelectorPage, self).__init__(parent, session, "Select Patient")
        
        self.notebook = wx.Notebook(self)

        self.old_patient_panel = PatientSearchPanel(self.notebook, self.session)
        self.notebook.AddPage(self.old_patient_panel, "Existing Patient")
        self.sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, border=5)

        self.new_patient_panel = PatientFormPanel(self.notebook)
        self.notebook.AddPage(self.new_patient_panel, "New Patient")

    def is_valid(self):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page == self.new_patient_panel:
            blanks, blanks_lst = self.new_patient_panel.check()
            if blanks:
                self.error_message = "Following fields cannot be empty\n{}".format("\n".join(blanks_lst))
                return False
            return True
        else:
            selected_patient = self.old_patient_panel.get_selected()
            if selected_patient is None:
                self.error_message = "No Patient Selected"
                return False
            return True

    def get_patient(self):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page == self.new_patient_panel:
            return self.new_patient_panel.get_object()
        else:
            return self.old_patient_panel.get_selected()


class DoctorBedSelectorPage(BasePage):
    def __init__(self, parent, session):
        super(DoctorBedSelectorPage, self).__init__(parent, session, "Select Bed")

        self.cmb_doctor = DbComboBox(self, self.session)
        self.cmb_doctor.set_items(
            self.session.query(db.Doctor)
        )

        self.cmb_ward = DbComboBox(self, self.session)
        self.cmb_ward.Bind(wx.EVT_COMBOBOX, self._on_change_ward)
        self.cmb_ward.set_items(
            self.session.query(db.Ward)
        )

        self.beds_list = DbQueryResultBox(self, self._bed_decorator)

        grid_sizer = wx.FlexGridSizer(3, 2, 5, 5)
        grid_sizer.AddMany([
            (wx.StaticText(self, label="Admitting Doctor"), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.cmb_doctor, 1, wx.EXPAND),
            (wx.StaticText(self, label="Ward"), 0, wx.ALIGN_CENTER_VERTICAL),
            (self.cmb_ward, 1, wx.EXPAND),
            (wx.StaticText(self, label="Bed"), 0, wx.ALIGN_CENTER_VERTICAL),
        ])
        grid_sizer.AddGrowableCol(1)

        self.sizer.Add(grid_sizer, 0 , wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        self.sizer.Add(self.beds_list, 1, wx.EXPAND | wx.ALL, border=5)

    def _bed_decorator(self, bed, query_string):
        html = '<font size="2">'\
                    '<table width="100%">'\
                        '<tr>'\
                            '<td valign="top">{0}</td>'\
                        '</tr>'\
                    '</table>'\
                '</font>'
        return html.format(str(bed))

    def _on_change_ward(self, event):
        selected_ward = self.cmb_ward.get_selected_item()

        if selected_ward is None:
            self.beds_list.clear()
        else:
            query_result = self.session.query(db.Bed)\
                                .filter(db.Bed.ward_id == selected_ward.id)#\
                                #.filter(db.Bed.admission == None)
            self.beds_list.set_result(query_result)

    def is_valid(self):
        selected_doc = self.cmb_doctor.get_selected_item()
        if selected_doc is None:
            self.error_message = "Select Admitting Doctor"
        selected_bed = self.beds_list.get_selected_object()
        if selected_bed is None:
            self.error_message = "Select a bed"
            return False
        return True

    def get_bed(self):
        return self.beds_list.get_selected_object()

    def get_doctor(self):
        return self.cmb_doctor.get_selected_item()


class ProblemSelectorPage(BasePage):
    def __init__(self, parent, session):
        super(ProblemSelectorPage, self).__init__(parent, session, "Add Diagnosis")


class NewAdmissionDialog(wx.wizard.Wizard):
    def __init__(self, parent, session, **kwds):
        super(NewAdmissionDialog, self).__init__(parent, **kwds)

        self.SetTitle("New Admission")

        self.SetPageSize((500, 400))

        self.pages = []

        self.session = session

        self.add_page(PatientSelectorPage(self, session))
        self.add_page(DoctorBedSelectorPage(self, session))
        #self.add_page(ProblemSelectorPage(self, session))

        self.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self._on_page_changing)
        self.Bind(wx.wizard.EVT_WIZARD_FINISHED, self._on_finish)


    def add_page(self, page):
        if self.pages:
            previous_page = self.pages[-1]
            page.SetPrev(previous_page)
            previous_page.SetNext(page)
        self.pages.append(page)


    def ShowModal(self):
        self.RunWizard(self.pages[0])


    def get_patient(self):
        return self.pages[0].get_patient()


    def get_bed(self):
        return self.pages[1].get_bed()


    def get_doctor(self):
        return self.pages[1].get_doctor()


    def _on_page_changing(self, event):
        if event.GetDirection():#Going Forward
            page = event.GetPage()
            if not page.is_valid():
                page.show_error()
                event.Veto()

    def _on_finish(self, event):
        self.SetReturnCode(wx.ID_OK)
