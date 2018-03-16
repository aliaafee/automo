import wx

class FormPanel(wx.ScrolledWindow):
    """Database  Form for Data Input/Modification"""
    def __init__(self, parent, db_object_class, fields, scrollable=True, style=wx.VSCROLL, **kwds):
        super(FormPanel, self).__init__(parent, style=style, **kwds)

        self.db_object = None
        self.db_object_class = db_object_class
        self.fields = fields

        sizer = wx.FlexGridSizer(len(self.fields), 3, 4, 4)
        for field in self.fields:
            label = field.create_label(self)
            sizer.Add(label, 0)#, wx.ALIGN_CENTER_VERTICAL)

            help_button = field.create_help_button(self)
            if help_button is None:
                sizer.AddSpacer(1)
            else:
                sizer.Add(help_button, 0, wx.EXPAND)
            
            editor = field.create_editor(self)
            sizer.Add(editor, 0, wx.EXPAND)

        sizer.AddGrowableCol(2)

        self.SetSizer(sizer)

        self.scrollable = scrollable

        if self.scrollable:
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

        self.Layout()


    def Layout(self):
        super(FormPanel, self).Layout()
        if self.scrollable:
            self.SetScrollbars(20,20,55,40)


    def lock(self):
        for field in self.fields:
            field.lock_editor()


    def unlock(self):
        for field in self.fields:
            field.unlock_editor()


    def check(self):
        invalid = False
        lst_invalid = []
        for field in self.fields:
            valid, message = field.is_valid()
            if not valid:
                invalid = True
                lst_invalid.append("   {0} ({1})".format(field.label, message))
        return invalid, lst_invalid


    def update_object(self, db_object):
        for field in self.fields:
            field.update_object(db_object)


    def get_object(self):
        new_object = self.db_object_class()

        for field in self.fields:
            setattr(new_object, field.str_attr, field.get_value())

        return new_object
