import wx

from .field import Field


class OptionsRelationField(Field):
    def __init__(self, label, str_attr, db_options_query, nonelabel="None", value_formatter=None, required=False, editable=True):
        super(OptionsRelationField, self).__init__(label, str_attr, required, editable)
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
