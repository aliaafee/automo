import wx

from .formpanel import FormPanel
from .. import events


class FormSwitcher(wx.Panel):
    """Create and display appropriate form for the class"""
    def __init__(self, parent, session, **kwds):
        super(FormSwitcher, self).__init__(parent, **kwds)

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
        if self.locked:
            self.active_form.lock()
        else:
            self.active_form.unlock()


    def update_object(self, db_object):
        if self.active_form is None:
            return
        self.active_form.update_object(db_object)


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
            self.panels[object_type] = FormPanel(self, object_class, fields, False)
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
