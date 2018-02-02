"""Database Form for Data Input/Modification"""
import wx

from .. import database as db
from . import events
from .basedialog import BaseDialog
from .pydatepickerctrl import PyDatePickerCtrl
from .pydatetimepickerctrl import PyDateTimePickerCtrl, EVT_DATETIME_CHANGED



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
        else:
            self.editor.Bind(wx.EVT_TEXT, self.on_editor_changed)
        return self.editor

    def lock_editor(self):
        self.editor.SetEditable(False)

    def unlock_editor(self):
        self.editor.SetEditable(True)

    #def bind_editor_onchange(self, callable_function):
    #    self.editor.Bind(wx.EVT_TEXT, callable_function)

    def on_editor_changed(self, event):
        """Editor changed"""
        changed_event = events.DbFormChangedEvent(object=self)
        wx.PostEvent(self.editor.GetParent(), changed_event)

    def create_label(self, parent):
        if self.required:
            label = "{}*".format(self.label)
        else:
            label = self.label
        return wx.StaticText(parent, label=label)

    def set_editor_value(self, value):
        if value is None:
            self.editor.ChangeValue("")
            return
        self.editor.ChangeValue(value)

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


class DbMultilineStringField(DbFormFieldDefn):
    def __init__(self, label, str_attr, lines=3, required=False, editable=True):
        super(DbMultilineStringField, self).__init__(label, str_attr, required, editable)
        self.lines = lines

    def create_editor(self, parent):
        self.editor = wx.TextCtrl(parent, style=wx.TE_MULTILINE, size=(-1, self.lines * 15))
        if not self.editable:
            self.editor.SetEditable(False)
        else:
            self.editor.Bind(wx.EVT_TEXT, self.on_editor_changed)
        return self.editor


class DbOptionalMultilineStringField(DbFormFieldDefn):
    def __init__(self, label, str_attr, lines=3, required=False, editable=True):
        super(DbOptionalMultilineStringField, self).__init__(label, str_attr, required, editable)
        self.lines = lines

    def _on_check(self, event):
        if self.checkbox.GetValue() is True:
            self.textbox.Show()
        else:
            self.textbox.Hide()
        self.parent.Layout()
        self.parent.SetScrollbars(20,20,55,40)
        self.on_editor_changed(event)

    def create_editor(self, parent):
        self.parent = parent
        
        self.editor = wx.Panel(parent)
        self.checkbox = wx.CheckBox(self.editor)
        self.textbox = wx.TextCtrl(self.editor, style=wx.TE_MULTILINE, size=(-1, self.lines * 15))

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.checkbox, 0, wx.RIGHT | wx.ALIGN_TOP, border=2),
        sizer.Add(self.textbox, 1, wx.EXPAND)
        self.editor.SetSizer(sizer)

        self.textbox.Hide()

        if not self.editable:
            self.lock_editor()
        else:
            self.checkbox.Bind(wx.EVT_CHECKBOX, self._on_check)
            self.textbox.Bind(wx.EVT_TEXT, self.on_editor_changed)

        return self.editor

    def lock_editor(self):
        self.checkbox.Disable()
        self.textbox.Disable()

    def unlock_editor(self):
        self.checkbox.Enable()
        self.textbox.Enable()

    def set_editor_value(self, value):
        if value is None:
            self.textbox.ChangeValue("")
            self.textbox.Hide()
            self.checkbox.SetValue(False)
            return
        self.textbox.ChangeValue(value)
        self.textbox.Show()
        self.checkbox.SetValue(True)

    def get_editor_value(self):
        if self.checkbox.GetValue() is False:
            return None
        str_value = self.textbox.GetValue()
        if str_value == "":
            return None
        return str_value


class DbOptionsField(DbFormFieldDefn):
    def __init__(self, label, str_attr, options=[], nonelabel="None", otherlabel="Specify", lines=3, required=False, editable=True):
        super(DbOptionsField, self).__init__(label, str_attr, required, editable)
        self.lines = lines
        self.options = options
        self.nonelabel = nonelabel
        self.otherlabel = otherlabel
        self.selection = -1

    def _on_radio_group(self, event):
        rb = event.GetEventObject()
        self.selection = self.radiobuttons.index(rb)
        if self.selection == len(self.radiobuttons) - 1:
            #Last item selected, so show entry box
            self.textbox.Show()
        else:
            self.textbox.Hide()
        self.on_editor_changed(event)
        self.parent.Layout()

    def create_editor(self, parent):
        self.parent = parent
        
        self.editor = wx.Panel(parent, style=wx.BORDER_THEME)
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.radiobuttons = []

        rb = wx.RadioButton(self.editor, label=self.nonelabel, style=wx.RB_GROUP)
        self.radiobuttons.append(rb)
        sizer.Add(rb, 0, wx.EXPAND | wx.ALL, border=4)

        for option in self.options:
            rb = wx.RadioButton(self.editor, label=option)
            self.radiobuttons.append(rb)
            sizer.Add(rb, 0, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, border=4)

        rb = wx.RadioButton(self.editor, label=self.otherlabel)
        self.radiobuttons.append(rb)
        sizer.Add(rb, 0, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, border=4)

        self.textbox = wx.TextCtrl(self.editor, style=wx.TE_MULTILINE, size=(-1, self.lines * 15))
        sizer.Add(self.textbox, 1, wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, border=4)
        self.editor.SetSizer(sizer)

        self.textbox.Hide()
        self.radiobuttons[0].SetValue(True)

        if not self.editable:
            self.lock_editor()
        else:
            self.editor.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX))
            self.editor.Bind(wx.EVT_RADIOBUTTON, self._on_radio_group)
            self.textbox.Bind(wx.EVT_TEXT, self.on_editor_changed)

        return self.editor

    def lock_editor(self):
        for rb in self.radiobuttons:
            rb.Disable()
        self.textbox.Disable()
        

    def unlock_editor(self):
        for rb in self.radiobuttons:
            rb.Enable()
        self.textbox.Enable()

    def set_editor_value(self, value):
        if value is None:
            self.selection = 0
            self.radiobuttons[self.selection].SetValue(True)
            self.textbox.ChangeValue("")
            self.textbox.Hide()
        elif value in self.options:
            index = self.options.index(value)
            self.selection = index + 1
            self.radiobuttons[self.selection].SetValue(True)
            self.textbox.ChangeValue("")
            self.textbox.Hide()
        else:
            self.selection = len(self.radiobuttons) - 1
            self.radiobuttons[self.selection].SetValue(True)
            self.textbox.ChangeValue(value)
            self.textbox.Show()

    def get_editor_value(self):
        if self.selection == 0:
            return None
        
        if self.selection < len(self.radiobuttons) - 1:
            index = self.selection - 1
            return self.options[index]

        str_value = self.textbox.GetValue()
        if str_value == "":
            return None

        return str_value


class DbOptionsRelationField(DbFormFieldDefn):
    def __init__(self, label, str_attr, db_options_query, nonelabel="None", value_formatter=None, required=False, editable=True):
        super(DbOptionsRelationField, self).__init__(label, str_attr, required, editable)
        self.nonelabel = nonelabel
        self.db_options_query = db_options_query
        self.value_formatter = value_formatter
        if value_formatter is None:
            self.value_formatter = self._value_formatter
        self.options = []
        self.selection = 0

    def _value_formatter(self, value):
        return unicode(value)

    def _on_radio_group(self, event):
        rb = event.GetEventObject()
        self.selection = self.radiobuttons.index(rb)
        self.on_editor_changed(event)

    def create_editor(self, parent):
        self.parent = parent

        self.editor = wx.Panel(parent, style=wx.BORDER_THEME)
        sizer = wx.FlexGridSizer(2, 4, 4)

        self.radiobuttons = []
        self.labels = []

        rb = wx.RadioButton(self.editor, label="", style=wx.RB_GROUP)
        self.radiobuttons.append(rb)
        sizer.Add(rb, 0, wx.ALIGN_TOP)
        lbl = wx.StaticText(self.editor)
        lbl.SetLabelMarkup(self.nonelabel)
        lbl.Wrap(300)
        sizer.Add(lbl, 1, wx.EXPAND)

        self.options = self.db_options_query.all()
        for index, option in enumerate(self.options):
            rb = wx.RadioButton(self.editor, label="")
            self.radiobuttons.append(rb)
            sizer.Add(rb, 0, wx.ALIGN_TOP)
            lbl = wx.StaticText(self.editor)
            lbl.SetLabelMarkup(self.value_formatter(option))
            lbl.Wrap(400)
            sizer.Add(lbl, 1, wx.EXPAND)

        self.radiobuttons[0].SetValue(True)

        sizer.AddGrowableCol(1)

        self.editor.SetSizer(sizer)

        if not self.editable:
            self.lock_editor()
        else:
            self.editor.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX))
            self.editor.Bind(wx.EVT_RADIOBUTTON, self._on_radio_group)

        return self.editor

    def lock_editor(self):
        for rb in self.radiobuttons:
            rb.Disable()     

    def unlock_editor(self):
        for rb in self.radiobuttons:
            rb.Enable()

    def get_editor_value(self):
        if self.selection == 0:
            return None

        index = self.selection - 1
        return self.options[index]

    def set_editor_value(self, value):
        if value is None:
            self.selection = 0
        elif value in self.options:
            index = self.options.index(value)
            self.selection = index + 1
        self.radiobuttons[self.selection].SetValue(True)


class DbCheckBoxField(DbFormFieldDefn):
    def __init__(self, label, str_attr, required=False, editable=True):
        super(DbCheckBoxField, self).__init__(label, str_attr, required, editable)


    def create_editor(self, parent):
        self.parent = parent
        
        self.editor = wx.CheckBox(self.parent, style=wx.CHK_3STATE | wx.CHK_ALLOW_3RD_STATE_FOR_USER)

        self.editor.Bind(wx.EVT_CHECKBOX, self.on_editor_changed)
        
        return self.editor

    def lock_editor(self):
        self.editor.Disable()
        
    def unlock_editor(self):
        self.editor.Enable()

    def set_editor_value(self, value):
        if value is None:
            self.editor.Set3StateValue(wx.CHK_UNDETERMINED)
        elif value is True:
            self.editor.Set3StateValue(wx.CHK_CHECKED)
        else:
            self.editor.Set3StateValue(wx.CHK_UNCHECKED)

    def get_editor_value(self):
        editor_value = self.editor.Get3StateValue()
        if editor_value == wx.CHK_UNDETERMINED:
            return None
        elif editor_value == wx.CHK_CHECKED:
            return True
        else:
            return False




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
        if not self.editable:
            self.editor.Disable()
        else:
            self.editor.Bind(wx.EVT_CHOICE, self.on_editor_changed)
        return self.editor

    def lock_editor(self):
        self.editor.Disable()

    def unlock_editor(self):
        self.editor.Enable()

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


class DbRelationField(DbEnumField):
    def __init__(self, label, str_attr, db_choices_query, value_formatter=None, required=False, editable=True):
        super(DbRelationField, self).__init__(label, str_attr, [], required, editable)
        self.db_choices_query = db_choices_query
        self.value_formatter = value_formatter
        if value_formatter is None:
            self.value_formatter = self._value_formatter
        self.choices = []

    def _value_formatter(self, value):
        return unicode(value)

    def _update_choices(self, value_search=None):
        self.choices = self.db_choices_query.all()
        choices_str = []
        selection = -1
        for index, choice in enumerate(self.choices):
            choices_str.append(self.value_formatter(choice))
            if choice == value_search:
                selection = index
        self.editor.SetItems(choices_str)
        self.editor.SetSelection(selection)

    def create_editor(self, parent):
        editor = super(DbRelationField, self).create_editor(parent)
        self._update_choices()
        return editor

    def set_editor_value(self, value):
        self._update_choices(value)

    def get_editor_value(self):
        selection = self.editor.GetSelection()
        if selection == -1:
            return None
        return self.choices[selection]


class DbDateField(DbFormFieldDefn):
    def __init__(self, label, str_attr, required=False, editable=True):
        super(DbDateField, self).__init__(label, str_attr, required, editable)

    def create_editor(self, parent):
        self.editor = PyDatePickerCtrl(parent, style=wx.DP_DROPDOWN | wx.DP_ALLOWNONE)
        if not self.editable:
            self.editor.Disable()
        else:
            self.editor.Bind(wx.EVT_DATE_CHANGED, self.on_editor_changed)
        return self.editor

    def lock_editor(self):
        self.editor.Disable()

    def unlock_editor(self):
        self.editor.Enable()

    def set_editor_value(self, value):
        self.editor.set_pydatetime(value)

    def get_editor_value(self):
        return self.editor.get_pydatetime()


class DbDateTimeField(DbFormFieldDefn):
    def __init__(self, label, str_attr, required=False, editable=True):
        super(DbDateTimeField, self).__init__(label, str_attr, required, editable)

    def create_editor(self, parent):
        self.editor = PyDateTimePickerCtrl(parent)
        if not self.editable:
            self.editor.Disable()
        else:
            self.editor.Bind(EVT_DATETIME_CHANGED, self.on_editor_changed)
        return self.editor

    def lock_editor(self):
        self.editor.Disable()

    def unlock_editor(self):
        self.editor.Enable()

    def set_editor_value(self, value):
        self.editor.set_pydatetime(value)

    def get_editor_value(self):
        return self.editor.get_pydatetime()


class DbAddressField(DbFormFieldDefn):
    def __init__(self, label, str_attr, required=False, editable=True):
        super(DbAddressField, self).__init__(label, str_attr, required, editable)
        self.fields = [
            DbStringField("Line 1", "line_1", editable=editable),
            DbStringField("Line 2", "line_2", editable=editable),
            DbStringField("Line 3", "line_3", editable=editable),
            DbStringField("City", "city", editable=editable),
            DbStringField("Region", "region", editable=editable),
            DbStringField("Country", "country", editable=editable)
        ]

    def create_editor(self, parent):
        self.editor = DbFormPanel(parent, db.Address, self.fields, scrollable=False, style=wx.BORDER_THEME)
        if self.editable:
            self.editor.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX))
        else:
            self.editor.Bind(events.EVT_AM_DB_FORM_CHANGED, self.on_editor_changed)
        return self.editor

    def lock_editor(self):
        self.editor.lock()

    def unlock_editor(self):
        self.editor.unlock()

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

        sizer = wx.FlexGridSizer(len(self.fields), 2, 4, 4)
        for field in self.fields:
            label = field.create_label(self)
            editor = field.create_editor(self)
            sizer.Add(label, 0)#, wx.ALIGN_CENTER_VERTICAL)
            sizer.Add(editor, 0, wx.EXPAND)
        sizer.AddGrowableCol(1)

        self.SetSizer(sizer)

        if scrollable:
            self.SetScrollbars(20,20,55,40)
        else:
            sizer.AddGrowableRow(len(self.fields) - 1)


    def set_object(self, db_object):
        self.db_object = db_object

        if self.db_object is None:
            for field in self.fields:
                field.clear()
            return

        for field in self.fields:
            field.set_object(db_object)

        self.SetScrollbars(20,20,55,40)
        self.Layout()


    def lock(self):
        for field in self.fields:
            field.lock_editor()


    def unlock(self):
        for field in self.fields:
            field.unlock_editor()


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



class DbFormSwitcher(wx.Panel):
    """Create and display appropriate form for the class"""
    def __init__(self, parent, session, **kwds):
        super(DbFormSwitcher, self).__init__(parent, **kwds)

        self.session = session

        self.active_form = None
        self.panels = {}

        self._prev_active_form = None

        self.locked = False

        self.sizer = wx.BoxSizer()
        self.SetSizer(self.sizer)


    def set_object(self, db_object, fields):
        """Show the appropriate form and set the data to the form"""
        self._show_form(db_object.type, db_object.__class__, fields)
        self.active_form.set_object(db_object)


    def update_object(self, db_object):
        if self.active_form is None:
            return
        self.active_form.update_object(db_object)
        if self.locked:
            self.active_form.lock()
        else:
            self.active_form.unlock()


    def unlock(self):
        if self.active_form is None:
            return
        self.active_form.unlock()
        self.locked = False


    def lock(self):
        if self.active_form is None:
            return
        self.active_form.lock()
        self.locked = True


    def unset_object(self):
        if self.active_form is None:
            return

        self.active_form.Hide()
        self.active_form = None


    def _on_field_changed(self, event):
        changed_event = events.DbFormChangedEvent(object=self)
        wx.PostEvent(self, changed_event)


    def _show_form(self, object_type, object_class, fields):
        if object_type not in self.panels.keys():
            self.panels[object_type] = DbFormPanel(self, object_class, fields, False)
            self.sizer.Add(self.panels[object_type], 1, wx.EXPAND | wx.ALL, border=5)
            self.panels[object_type].Bind(events.EVT_AM_DB_FORM_CHANGED, self._on_field_changed)

        self.active_form = self.panels[object_type]

        for name, panel in self.panels.items():
            if panel == self.active_form:
                panel.Show()
            else:
                panel.Hide()

        if self.active_form != self._prev_active_form:
            self.Layout()
            self._prev_active_form = self.active_form

        return self.active_form



class DbFormDialog(BaseDialog):
    """Database  Form Dialog for Data Input/Modification"""
    def __init__(self, parent, db_object_class, fields,  **kwds):
        super(DbFormDialog, self).__init__(parent, **kwds)
        self.form = DbFormPanel(self, db_object_class, fields)
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
