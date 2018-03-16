"""Form Page"""
import wx

from .. import dbform as fm
from ..newadmissionwizard.basepage import BasePage


class FormPage(BasePage):
    """Form Page"""
    def __init__(self, parent, session, title, db_object_class, fields, scrollable=True):
        super(FormPage, self).__init__(parent, session, title)

        self.form_panel = fm.FormPanel(self, db_object_class, fields, scrollable)
        self.sizer.Add(self.form_panel, 1, wx.ALL | wx.EXPAND, border=5)


    def is_valid(self):
        invalid, lst_invalid = self.form_panel.check()
        if invalid:
            self.error_message = "Following fields are not valid:\n\n{}".format("\n".join(lst_invalid))
            return False
        return True


    def set_object(self, db_object):
        self.form_panel.set_object(db_object)


    def update_db_object(self, db_object):
        self.form_panel.update_object(db_object)
