"""Problems Selector"""
import wx

from ... import database as db
from .. import images
from ..dblistbox import DbListBox
from ..icd10coder import Icd10Coder
from ..problempanel import problems_decorator
from .basepage import BasePage


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
