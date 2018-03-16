import wx

from ..basedialog import BaseDialog
from .formpanel import FormPanel


class FormDialog(BaseDialog):
    """Database  Form Dialog for Data Input/Modification"""
    def __init__(self, parent, db_object_class, fields,  **kwds):
        super(FormDialog, self).__init__(parent, **kwds)
        self.form = FormPanel(self, db_object_class, fields)
        self.add_to_sizer(self.form, 1, wx.EXPAND)


    def set_object(self, db_object):
        self.form.set_object(db_object)


    def update_object(self, db_object):
        self.form.update_object(db_object)


    def get_object(self):
        return self.form.get_object()


    def on_ok(self, event):
        blanks, lst_blanks = self.form.check()
        if blanks:
            dlg = wx.MessageDialog(
                None,
                "Following fields cannot be empty:\n   {}".format("\n   ".join(lst_blanks)),
                "Required Fields are Empty",
                wx.OK | wx.ICON_ERROR
            )
            dlg.ShowModal()
            dlg.Destroy()
            return
        self.EndModal(wx.ID_OK)
