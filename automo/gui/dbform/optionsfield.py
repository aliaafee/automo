import wx

from .field import Field


class OptionsField(Field):
    def __init__(self, label, str_attr, options=[], nonelabel="None", otherlabel="Specify", lines=3, required=False, editable=True):
        super(OptionsField, self).__init__(label, str_attr, required, editable)
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
