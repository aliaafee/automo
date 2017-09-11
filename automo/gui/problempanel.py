"""Problem Panel"""
import wx

from .. import config
from .. import database as db
from . import events
from . import images
from .icd10coder import Icd10Coder
from .dblistbox import DbListBox


class ProblemPanel(wx.Panel):
    """Problem Panel"""
    def __init__(self, parent, session, **kwds):
        super(ProblemPanel, self).__init__(parent, **kwds)

        self.session = session
        self.encounter = None

        self.editable = True

        sizer = wx.BoxSizer(wx.VERTICAL)

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)

        tb_add = self.toolbar.AddLabelTool(
            wx.ID_ADD,
            label="Add",
            bitmap=images.get("add_condition"),
            shortHelp="Add Condition"
        )
        self.Bind(wx.EVT_TOOL, self._on_add_problem, tb_add)

        """
        tb_add_quick = self.toolbar.AddLabelTool(
            wx.ID_ANY,
            label="Add Quick Search",
            bitmap=images.get("add_problem_quick"),
            shortHelp="Add Condition from Quick Search"
        )
        self.Bind(wx.EVT_TOOL, self._on_add_quick, tb_add_quick)

        tb_add_favourite = self.toolbar.AddLabelTool(
            wx.ID_ANY,
            label="Add Favourite",
            bitmap=images.get("add_problem_favourite"),
            shortHelp="Add Condition from Favourites"
        )
        self.Bind(wx.EVT_TOOL, self._on_add_favourite, tb_add_favourite)
        """

        self.toolbar.Realize()
        sizer.Add(self.toolbar, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT,
                  border=5)

        self.problems_list = DbListBox(self, self._problems_decorator, style=wx.LB_MULTIPLE)
        self.problems_list.Bind(wx.EVT_RIGHT_DOWN, self._on_problems_context)
        sizer.Add(self.problems_list, 1, wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(sizer)

        self.icd10_coder = Icd10Coder(self, self.session)

        self.problems_menu = wx.Menu()
        self.problems_menu.Append(wx.ID_REMOVE, "Remove", "Remove Selected Conditions.")
        self.problems_menu.Bind(wx.EVT_MENU, self._on_remove_problems, id=wx.ID_REMOVE)



    def _problems_decorator(self, problem_object):
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
            problem_object.icd10class_code,
            problem_object.icd10class.preferred_plain,
            comment,
            modifer_str
        )


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
            new_problem = db.Problem()
            self.encounter.patient.problems.append(new_problem)
            new_problem.icd10class = self.icd10_coder.selected_icd10class
            new_problem.icd10modifier_class = self.icd10_coder.selected_modifier_class
            new_problem.icd10modifier_extra_class = self.icd10_coder.selected_modifier_extra_class
            new_problem.comment = self.icd10_coder.selected_comment
            new_problem.start_time = self.icd10_coder.selected_start_time
            self.session.add(new_problem)
            self.encounter.add_problem(new_problem)
            self.session.commit()
            self.set_encounter(self.encounter)

            new_event = events.EncounterChangedEvent(events.ID_ENCOUNTER_CHANGED, object=new_problem) 
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


    def set_editable(self, editable):
        """Set control to editable or not"""
        if editable:
            self.toolbar.Show()
        else:
            self.toolbar.Hide()

        if self.editable != editable:
            self.Layout()

        self.editable = editable

    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing.
          Always false in this panel as all changes are autosaved"""
        return False


    def save_changes(self):
        """Save changes. Everything is auto saved."""
        pass


    def set_encounter(self, encounter):
        """Set the current encounter"""
        self.encounter = encounter

        self.problems_list.set_items(self.encounter.problems)
