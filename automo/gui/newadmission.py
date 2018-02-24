"""New Admission Wizard"""
import wx
import wx.adv

from .. import database as db
from . import images
from .dbcombobox import DbComboBox
from .patientinfo import PatientFormPanel
from .dbqueryresultbox import DbQueryResultBox
from .patientsearchpanel import PatientSearchPanel
from .dblistbox import DbListBox
from .problempanel import problems_decorator
from .icd10coder import Icd10Coder


class BasePage(wx.adv.WizardPage):
    """Base for all Wizard Pages"""
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

    def set(self):
        pass

    def must_skip(self):
        return False

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next

    def GetPrev(self):
        return self.prev


class PatientSelectorPage(BasePage):
    """Select the patient, TODO: Handle Duplicate Patients"""
    def __init__(self, parent, session):
        super(PatientSelectorPage, self).__init__(parent, session, "Select Patient")

        self.new_patient = db.Patient()
        
        self.notebook = wx.Notebook(self)

        self.old_patient_panel = PatientSearchPanel(self.notebook, self.session)
        self.notebook.AddPage(self.old_patient_panel, "Existing Patient")
        self.sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, border=5)

        self.new_patient_panel = PatientFormPanel(self.notebook)
        self.notebook.AddPage(self.new_patient_panel, "New Patient")

    def is_valid(self):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page == self.new_patient_panel:
            invalid, lst_invalid = self.new_patient_panel.check()
            if invalid:
                self.error_message = "Following fields are not valid:\n\n{}".format("\n".join(lst_invalid))
                return False
            return True
        else:
            selected_patient = self.old_patient_panel.get_selected()
            if selected_patient is None:
                self.error_message = "No Patient Selected"
                return False
            current_encounter = selected_patient.get_current_encounter(self.session)
            if current_encounter is not None:
                self.error_message = "This patient already has an active encounter. Cannot admit before ending all active encounters."
                return False
            return True

    def get_patient(self):
        active_page = self.notebook.GetPage(self.notebook.GetSelection())
        if active_page == self.new_patient_panel:
            self.new_patient_panel.update_object(self.new_patient)
            return self.new_patient
        else:
            return self.old_patient_panel.get_selected()


class DoctorBedSelectorPage(BasePage):
    """Select Doctor and Bed"""
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
                                .filter(db.Bed.ward_id == selected_ward.id)\
                                .filter(db.Bed.admission == None)
            self.beds_list.set_result(query_result)

    def is_valid(self):
        selected_doc = self.cmb_doctor.get_selected_item()
        if selected_doc is None:
            self.error_message = "Select Admitting Doctor"
            return False
        selected_bed = self.beds_list.get_selected_object()
        if selected_bed is None:
            self.error_message = "Select a bed"
            return False
        return True

    def get_bed(self):
        return self.beds_list.get_selected_object()

    def get_doctor(self):
        return self.cmb_doctor.get_selected_item()


ID_ADD_NEW = wx.NewId()
ID_ADD_EXISTING = wx.NewId()
ID_REMOVE = wx.NewId()

class ProblemSelectorPage(BasePage):
    """Problems Selector"""
    def __init__(self, parent, session):
        super(ProblemSelectorPage, self).__init__(parent, session, "Diagnosis")

        self.patient = None

        self.all_problems = [] #self.session.query(db.Problem).filter(db.Problem.patient == self.patient).all()
        self.selected_problems = []

        self.delete_image = images.get("delete")
        self.right_arrow = images.get("right_double_arrow")
        self.left_arrow = images.get("left_double_arrow")
        self.blank = images.get("blank")

        self.toolbar = wx.ToolBar(self, style=wx.TB_VERTICAL | wx.TB_NODIVIDER)
        self.toolbar.AddTool(ID_ADD_NEW, "Add New", images.get("add_condition"), wx.NullBitmap, wx.ITEM_NORMAL, "Add New Problem", "")
        self.toolbar.AddTool(ID_ADD_EXISTING, "Add Existing", self.left_arrow, wx.NullBitmap, wx.ITEM_NORMAL, "Add Existing Problem", "")
        self.toolbar.AddTool(ID_REMOVE, "Remove", self.right_arrow, wx.NullBitmap, wx.ITEM_NORMAL, "Remove Problem", "")
        self.toolbar.Realize()

        self.toolbar.Bind(wx.EVT_TOOL, self._on_add_new, id=ID_ADD_NEW)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_remove, id=ID_REMOVE)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_add_existing, id=ID_ADD_EXISTING)

        self.all_problems_list = DbListBox(self, problems_decorator)
        self.selected_problems_list = DbListBox(self, problems_decorator)

        self.lbl_existing = wx.StaticText(self, label="Existing Problems")
        self.lbl_selected = wx.StaticText(self, label="Selected Problems")

        gridsizer = wx.FlexGridSizer(2, 3, 2, 2)
        gridsizer.Add(self.lbl_existing, 1, wx.ALIGN_CENTER_HORIZONTAL)
        gridsizer.AddSpacer(2)
        gridsizer.Add(self.lbl_selected, 1, wx.ALIGN_CENTER_HORIZONTAL)
        gridsizer.AddMany([
            (self.all_problems_list, 1, wx.EXPAND),
            (self.toolbar, 1, wx.ALIGN_TOP),
            (self.selected_problems_list, 1, wx.EXPAND)
        ])
        gridsizer.AddGrowableCol(0)
        gridsizer.AddGrowableCol(2)
        gridsizer.AddGrowableRow(1)
        self.sizer.Add(gridsizer, 1, wx.EXPAND)
        self.Layout()

    def _on_add_new(self, event):
        self.icd10_coder = Icd10Coder(self, self.session)
        self.icd10_coder.CenterOnScreen()
        if self.icd10_coder.ShowModal() == wx.ID_OK:
            new_problem = self.icd10_coder.get_problem()
            self.selected_problems.append(new_problem)
            self._update_selected_problems()
        self.icd10_coder.Destroy()

    def _on_remove(self, event):
        selection = self.selected_problems_list.get_selected_object()
        try:
            self.selected_problems.remove(selection)
        except ValueError:
            pass
        else:
            self._update_selected_problems()
            if selection in self.all_problems:
                self._update_all_problems()

    def _on_add_existing(self, event):
        selection = self.all_problems_list.get_selected_object()
        if selection is not None:
            self.selected_problems.append(selection)
            self._update_all_problems()
            self._update_selected_problems()

    def _update_all_problems(self):
        visible = [x for x in self.all_problems if x not in self.selected_problems]
        self.all_problems_list.set_items(visible)

    def _update_selected_problems(self):
        self.selected_problems_list.set_items(self.selected_problems)

    def set(self):
        patient = self.Parent.get_patient()
        if patient != self.patient:
            self.selected_problems = []
            self.patient = patient
            self.lbl_existing.Hide()
            self.all_problems_list.Hide()
            self.toolbar.EnableTool(ID_ADD_EXISTING, False)
            self.toolbar.SetToolNormalBitmap(ID_ADD_EXISTING, self.blank)
            self.toolbar.SetToolShortHelp(ID_ADD_EXISTING, "")
            self.toolbar.SetToolNormalBitmap(ID_REMOVE, self.delete_image)
            if patient in self.session:
                self.all_problems = self.session.query(db.Problem).filter(db.Problem.patient == patient).all()
                if self.all_problems:
                    self.lbl_existing.Show()
                    self.all_problems_list.Show()
                    self.toolbar.EnableTool(ID_ADD_EXISTING, True)
                    self.toolbar.SetToolNormalBitmap(ID_ADD_EXISTING, self.left_arrow)
                    self.toolbar.SetToolShortHelp(ID_ADD_EXISTING, "Add Existing Problem")
                    self.toolbar.SetToolNormalBitmap(ID_REMOVE, self.right_arrow)
                    self._update_all_problems()
            self.Layout()
            self._update_selected_problems()

    def is_valid(self):
        if not self.selected_problems:
            self.error_message = "Select at least one diagnosis."
            return False
        return True

    def get_problems(self):
        return self.selected_problems


class NewAdmissionDialog(wx.adv.Wizard):
    """New Admission Wizard"""
    def __init__(self, parent, session, patient=None, **kwds):
        super(NewAdmissionDialog, self).__init__(
            parent,
            style=wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION,
            **kwds)

        self.SetTitle("New Admission")

        self.SetPageSize((500, 400))

        self.pages = []

        self.session = session
        self.patient = patient

        if self.patient is None:
            self.patient_selector = PatientSelectorPage(self, session)
            self.add_page(self.patient_selector)

        self.doctorbed_selector = DoctorBedSelectorPage(self, session)
        self.add_page(self.doctorbed_selector)

        self.problem_selector = ProblemSelectorPage(self, session)
        self.add_page(self.problem_selector)

        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGING, self._on_page_changing)
        self.Bind(wx.adv.EVT_WIZARD_PAGE_CHANGED, self._on_page_changed)
        self.Bind(wx.adv.EVT_WIZARD_FINISHED, self._on_finish)


    def add_page(self, page):
        if self.pages:
            previous_page = self.pages[-1]
            page.SetPrev(previous_page)
            previous_page.SetNext(page)
        self.pages.append(page)


    def ShowModal(self):
        self.RunWizard(self.pages[0])


    def get_patient(self):
        if self.patient is not None:
            return self.patient
        return self.patient_selector.get_patient()


    def get_bed(self):
        return self.doctorbed_selector.get_bed()


    def get_doctor(self):
        return self.doctorbed_selector.get_doctor()


    def get_problems(self):
        return self.problem_selector.get_problems()


    def _on_page_changing(self, event):
        if event.GetDirection():#Going Forward
            page = event.GetPage()
            if not page.is_valid():
                page.show_error()
                event.Veto()


    def _on_page_changed(self, event):
        page = event.GetPage()
        page.set()


    def _on_finish(self, event):
        self.SetReturnCode(wx.ID_OK)
