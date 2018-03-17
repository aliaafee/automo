"""Problem Panel"""
import wx

from ... import config
from .. import events
from .. import images
from ..icd10coder import Icd10Coder
from ..widgets import DbListBox
from ..problempickerdialog import ProblemPickerDialog
from .encounternotebookpage import EncounterNotebookPage


def problems_decorator(problem_object):
    if problem_object.comment is None or problem_object.comment == "":
        comment = ""
    else:
        comment = "<tr><td></td><td></td><td>({0})</td></tr>".format(problem_object.comment)
    modifer_cls_strs = []
    for modifer_cls in [problem_object.icd10modifier_class,
                        problem_object.icd10modifier_extra_class]:
        if modifer_cls is not None:
            modifer_cls_strs.append(
                '<tr><td></td><td></td><td>{0}: {1} - {2}</td></tr>'.format(
                    modifer_cls.modifier.name,
                    modifer_cls.code_short,
                    modifer_cls.preferred
                )
            )
    modifer_str = "".join(modifer_cls_strs)

    html = u'<font size="2"><table width="100%">'\
                '<tr>'\
                    '<td valign="top" width="50">{0}</td>'\
                    '<td valign="top" width="40"><b>{1}</b></td>'\
                    '<td valign="top"><b>{2}</b></td>'\
                    '{4}'\
                    '{3}'\
                '</tr>'\
            '</table></font>'

    return html.format(
        config.format_date(problem_object.start_time),
        problem_object.icd10class.code,
        problem_object.icd10class.preferred_plain,
        comment,
        modifer_str
    )

ID_PRE_EXISTING = wx.NewId()


class ProblemPanel(EncounterNotebookPage):
    """Problem Panel"""
    def __init__(self, parent, session, **kwds):
        super(ProblemPanel, self).__init__(parent, session, **kwds)

        self.toolbar.SetWindowStyleFlag(wx.TB_HORZ_TEXT | wx.TB_FLAT | wx.TB_NODIVIDER)

        self.toolbar.AddTool(
            wx.ID_ADD,
            label="Add",
            bitmap=images.get("add_condition"),
            shortHelp="Add Condition"
        )
        self.Bind(wx.EVT_TOOL, self._on_add_problem, id=wx.ID_ADD)

        self.toolbar.AddTool(
            ID_PRE_EXISTING,
            label="Add Pre-existing",
            bitmap=images.get("add_condition"),
            shortHelp="Add Pre-existing Condition"
        )
        self.Bind(wx.EVT_TOOL, self._on_add_preexisting_problem, id=ID_PRE_EXISTING)

        self.toolbar.Realize()

        self.problems_list = DbListBox(self, problems_decorator, style=wx.LB_MULTIPLE)
        self.problems_list.Bind(wx.EVT_RIGHT_DOWN, self._on_problems_context)
        
        self.sizer.Add(self.problems_list, 1, wx.EXPAND | wx.ALL, border=5)

        self.icd10_coder = Icd10Coder(self, self.session)

        self.problems_menu = wx.Menu()
        self.problems_menu.Append(wx.ID_REMOVE, "Remove", "Remove Selected Conditions.")
        self.problems_menu.Bind(wx.EVT_MENU, self._on_remove_problems, id=wx.ID_REMOVE)


    def _on_add_problem(self, event):
        """Add Condition with Full Icd10 Coder"""
        if self.encounter is None:
            return

        if self.encounter.end_time is None:
            start_time = None
        else:
            start_time = self.encounter.start_time

        self.icd10_coder.CenterOnScreen()
        if self.icd10_coder.ShowModal(start_time=start_time) == wx.ID_OK:
            new_problem = self.icd10_coder.get_problem()
            self.encounter.patient.problems.append(new_problem)
            self.session.add(new_problem)
            self.encounter.add_problem(new_problem)
            self.session.commit()
            self.set_encounter(self.encounter)

            new_event = events.EncounterChangedEvent(events.ID_ENCOUNTER_CHANGED, object=new_problem) 
            wx.PostEvent(self, new_event)


    def _on_add_preexisting_problem(self, event):
        with ProblemPickerDialog(self, self.session, self.encounter, problems_decorator) as dlg:
            dlg.CenterOnScreen()
            if dlg.ShowModal() == wx.ID_OK:
                selected_problems = dlg.get_selected_problems()
                for problem in selected_problems:
                    self.encounter.add_problem(problem)
                self.session.commit()
                self.set_encounter(self.encounter)

                new_event = events.EncounterChangedEvent(events.ID_ENCOUNTER_CHANGED, object=problem) 
                wx.PostEvent(self, new_event)


    def _on_add_quick(self, event):
        """Add Condition with Full Icd10 Coder"""
        pass


    def _on_add_favourite(self, event):
        """Add Condition with Full Icd10 Coder"""
        pass

    def _on_problems_context(self, event):
        if not self.editable:
            return

        self.PopupMenu(self.problems_menu)


    def _on_remove_problems(self, event):
        with wx.MessageDialog(self, 'Remove selected problems?', 'Remove Conditions',
                              wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) as dlg:
            dlg.CenterOnParent()
            result = dlg.ShowModal()

            if result != wx.ID_YES:
                return

            selected = self.problems_list.get_all_selected_object()
            for problem in selected:
                self.encounter.remove_problem(problem)

            self.session.commit()

            new_event = events.EncounterChangedEvent(events.ID_ENCOUNTER_CHANGED, object=None) 
            wx.PostEvent(self, new_event)

            self.problems_list.set_items(self.encounter.problems)


    def set_encounter(self, encounter):
        """Set the current encounter"""
        self.encounter = encounter

        self.problems_list.set_items(self.encounter.problems)

