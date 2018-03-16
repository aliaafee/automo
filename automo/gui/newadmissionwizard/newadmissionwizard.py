"""New Admission Wizard"""
import wx

from .patientselectorpage import PatientSelectorPage
from .doctorbedselector import DoctorBedSelectorPage
from .problemselectorpage import ProblemSelectorPage



class NewAdmissionWizard(wx.adv.Wizard):
    """New Admission Wizard"""
    def __init__(self, parent, session, patient=None, **kwds):
        super(NewAdmissionWizard, self).__init__(
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
