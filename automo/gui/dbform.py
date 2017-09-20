"""Database Form for Data Input/Modification"""
import wx

from .basedialog import BaseDialog
from .pydatepickerctrl import PyDatePickerCtrl
from .. import database as db


class DbFormFieldDefn(object):
    def __init__(self, label, str_attr, required=False, editable=True):
        self.label = label
        self.str_attr = str_attr
        self.editable = editable
        self.editor = None
        self.db_object = None
        self.required = required

    def create_editor(self, parent):
        self.editor = wx.TextCtrl(parent)
        if not self.editable:
            self.editor.SetEditable(False)
        return self.editor

    def create_label(self, parent):
        if self.required:
            label = "{}*".format(self.label)
        else:
            label = self.label
        return wx.StaticText(parent, label=label)

    def set_editor_value(self, value):
        if value is None:
            self.editor.SetValue("")
            return
        self.editor.SetValue(value)

    def get_editor_value(self):
        value_str = self.editor.GetValue()
        if value_str == "":
            return None
        return value_str

    def clear(self):
        self.set_editor_value(None)

    def set_object(self, db_object):
        self.db_object = db_object
        value = getattr(self.db_object, self.str_attr)
        self.set_editor_value(value)

    def update_object(self, db_object):
        setattr(db_object, self.str_attr, self.get_value())

    def get_value(self):
        return self.get_editor_value()


class DbStringField(DbFormFieldDefn):
    def __init__(self, label, str_attr, required=False, editable=True):
        super(DbStringField, self).__init__(label, str_attr, required, editable)


class DbFloatField(DbFormFieldDefn):
    def __init__(self, label, str_attr, required=False, editable=True):
        super(DbFloatField, self).__init__(label, str_attr, required, editable)

    def set_editor_value(self, value):
        self.editor.SetValue(unicode(value))

    def get_editor_value(self):
        value_str = self.editor.GetValue()
        if value_str == "":
            return None
        try:
            return float(value_str)
        except ValueError:
            return None


class DbEnumField(DbFormFieldDefn):
    def __init__(self, label, str_attr, choices, required=False, editable=True):
        super(DbEnumField, self).__init__(label, str_attr, required, editable)
        self.choices = choices

    def create_editor(self, parent):
        self.editor = wx.Choice(parent)
        self.editor.SetItems(self.choices)
        return self.editor

    def set_editor_value(self, value):
        if value in self.choices:
            index = self.choices.index(value)
            self.editor.SetSelection(index)
        else:
            self.editor.SetSelection(-1)

    def get_editor_value(self):
        selection = self.editor.GetSelection()
        if selection != -1:
            return self.choices[selection]
        return None


class DbDateField(DbFormFieldDefn):
    def __init__(self, label, str_attr, required=False, editable=True):
        super(DbDateField, self).__init__(label, str_attr, required, editable)

    def create_editor(self, parent):
        self.editor = PyDatePickerCtrl(parent, style=wx.DP_DROPDOWN | wx.DP_ALLOWNONE)
        return self.editor

    def set_editor_value(self, value):
        self.editor.set_pydatetime(value)

    def get_editor_value(self):
        return self.editor.get_pydatetime()


class DbAddressField(DbFormFieldDefn):
    def __init__(self, label, str_attr, required=False, editable=True):
        super(DbAddressField, self).__init__(label, str_attr, required, editable)
        self.fields = [
            DbStringField("Line 1", "line_1"),
            DbStringField("Line 2", "line_2"),
            DbStringField("Line 3", "line_3"),
            DbStringField("City", "city"),
            DbStringField("Region", "region"),
            DbStringField("Country", "region")
        ]

    def create_editor(self, parent):
        self.editor = DbFormPanel(parent, db.Address, self.fields, scrollable=False, style=wx.BORDER_THEME)
        self.editor.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_LISTBOX))
        return self.editor

    def set_editor_value(self, value):
        self.editor.set_object(value)

    def get_editor_value(self):
        return self.editor.get_object()


class DbFormPanel(wx.ScrolledWindow):
    """Database  Form for Data Input/Modification"""
    def __init__(self, parent, db_object_class, fields, scrollable=True, style=wx.VSCROLL, **kwds):
        super(DbFormPanel, self).__init__(parent, style=style, **kwds)

        self.db_object = None
        self.db_object_class = db_object_class
        self.fields = fields

        sizer = wx.FlexGridSizer(len(self.fields), 2, 2, 2)
        for field in self.fields:
            label = field.create_label(self)
            editor = field.create_editor(self)
            sizer.Add(label, 0, wx.ALIGN_CENTER_VERTICAL)
            sizer.Add(editor, 0, wx.EXPAND)
        sizer.AddGrowableCol(1)

        self.SetSizer(sizer)

        if scrollable:
            self.SetScrollbars(20,20,55,40)


    def set_object(self, db_object):
        self.db_object = db_object

        if self.db_object is None:
            for field in self.fields:
                field.clear()
            return

        for field in self.fields:
            field.set_object(db_object)


    def check(self):
        blanks = False
        lst_blanks = []
        for field in self.fields:
            if field.required and field.get_value() is None:
                blanks = True
                lst_blanks.append(field.label)
        return blanks, lst_blanks


    def update_object(self, db_object):
        for field in self.fields:
            field.update_object(db_object)


    def get_object(self):
        new_object = self.db_object_class()

        for field in self.fields:
            setattr(new_object, field.str_attr, field.get_value())

        return new_object



class DbFormDialog(BaseDialog):
    """Database  Form Dialog for Data Input/Modification"""
    def __init__(self, parent, db_object_class, fields,  **kwds):
        super(DbFormDialog, self).__init__(parent, **kwds)
        self.form = DbFormPanel(self, db_object_class, fields)
        self.setup_sizers()


    def setup_contents(self):
        self.content_sizer.Add(self.form, 1, wx.EXPAND | wx.ALL, border=5)


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
