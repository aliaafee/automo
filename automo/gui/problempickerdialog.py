"""Problem Picker Dialog"""
import datetime
import wx

from .. import database as db
from .basedialog import BaseDialog
from .widgets import DbListBox, PyDateTimePickerCtrl


class ProblemPickerDialog(BaseDialog):
    """Choose Preexisting Problems"""
    def __init__(self, parent, session, encounter, problems_decorator, title="Pre-exisitng Problems", size=(500, 600), **kwds):
        super(ProblemPickerDialog, self).__init__(parent, title=title, size=size, **kwds)

        self.set_ok_label("Add")

        self.problems_list = DbListBox(self, problems_decorator, style=wx.LB_MULTIPLE)

        result = session.query(db.Problem)\
                    .filter(db.Problem.patient == encounter.patient)

        problems = []
        for problem in result:
            if encounter not in problem.encounters:
                problems.append(problem)

        self.problems_list.set_items(problems)

        self.add_to_sizer(self.problems_list, 1, wx.EXPAND)


    def get_selected_problems(self):
        return self.problems_list.get_all_selected_object()
