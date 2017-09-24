"""List with Form View for Subencounters"""
from datetime import datetime
import wx

from .. import config
from . import images
from . import events
from .dbqueryresultbox import DbQueryResultBox
from .dbform import DbFormPanel
from .encounternotebookpage import EncounterNotebookPage


class EncounterNotebookList(EncounterNotebookPage):
    """List with Form View for Subencounters"""
    def __init__(self, parent, session, db_subencounter_class, fields, **kwds):
        super(EncounterNotebookList, self).__init__(parent, session, **kwds)

        self.subencounter = None
        self.fields = fields
        self.db_subencounter_class = db_subencounter_class

        self.changed = False

        self.toolbar.AddLabelTool(wx.ID_ADD, "Add", images.get("add"), wx.NullBitmap, wx.ITEM_NORMAL, "Add", "")
        self.toolbar.AddSeparator()
        self.toolbar.AddLabelTool(wx.ID_SAVE, "Save", images.get("save"), wx.NullBitmap, wx.ITEM_NORMAL, "Save changes", "")
        self.toolbar.Realize()

        self.toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_save, id=wx.ID_SAVE)

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self.subencounter_list = DbQueryResultBox(splitter, self.subencounter_list_decorator)
        self.subencounter_list.Bind(wx.EVT_LISTBOX, self._on_subencounter_selected)

        self._left_panel = wx.Panel(splitter, style=wx.BORDER_THEME)

        self.subencounter_form = DbFormPanel(self._left_panel, db_subencounter_class, fields, scrollable=False)
        self.subencounter_form.Bind(events.EVT_AM_DB_FORM_CHANGED, self._on_field_changed)

        sizer = wx.BoxSizer()
        sizer.Add(self.subencounter_form, 1, wx.EXPAND | wx.ALL, border=5)
        self._left_panel.SetSizer(sizer)
        splitter.SplitVertically(self.subencounter_list, self._left_panel, 200)
        self.sizer.Add(splitter, 1, wx.EXPAND | wx.ALL, border=5)

        self.subencounter_form.Hide()


    def subencounter_list_decorator(self, encounter_object, query_string):
        """Decorator of Subencounter List"""
        date_str = config.format_date(encounter_object.start_time)
        html = u'<font size="2"><table width="100%">'\
                    '<tr>'\
                        '<td valign="top">&bull;</td>'\
                        '<td valign="top" width="100%"><b>{0}</b></td>'\
                    '</tr>'\
                '</table></font>'

        return html.format(date_str)


    def _on_field_changed(self, event):
        self.changed = True
        self._update_toolbar()


    def _on_add(self, event):
        if self.encounter is None:
            return

        if self.is_unsaved():
            self.save_changes()

        new_subencounter = self.db_subencounter_class()
        new_subencounter.start_time = datetime.now()
        new_subencounter.end_time = new_subencounter.start_time
        self.encounter.add_child_encounter(new_subencounter)
        self.session.commit()
        self.set_encounter(self.encounter)
        self.set_subencounter(new_subencounter)


    def _on_save(self, event):
        self.save_changes()

    def _update_toolbar(self):
        if self.changed:
            self.toolbar.EnableTool(wx.ID_SAVE, True)
        else:
            self.toolbar.EnableTool(wx.ID_SAVE, False)

    def is_unsaved(self):
        if self.encounter is not None and self.subencounter is not None:
            if self.changed:
                return True
        return False


    def save_changes(self):
        if self.encounter is not None and self.subencounter is not None:
            self.subencounter_form.update_object(self.subencounter)
            self.session.commit()
            self.set_subencounter(self.subencounter)
            self.subencounter_list.RefreshAll()


    def _on_subencounter_selected(self, event):
        if self.changed:
            self.save_changes()
            
        selected = self.subencounter_list.get_selected_object()

        self.set_subencounter(selected)


    def editable_on(self):
        super(EncounterNotebookList, self).editable_on()
        self.subencounter_form.unlock()


    def editable_off(self):
        super(EncounterNotebookList, self).editable_off()
        self.subencounter_form.lock()



    def set_subencounter(self, subencounter):
        self.subencounter = subencounter

        if subencounter is None:
            self.subencounter_form.Hide()

        self.subencounter_form.Show()
        self.subencounter_form.set_object(self.subencounter)

        self.changed = False
        self._update_toolbar()

        self._left_panel.Layout()


    def set_encounter(self, encounter):
        selection = -1
        if self.encounter is not None and self.encounter == encounter:
            selection = self.subencounter_list.GetSelection()

        super(EncounterNotebookList, self).set_encounter(encounter)

        result = self.session.query(self.db_subencounter_class)\
                    .filter(self.db_subencounter_class.parent == self.encounter)\
                    .order_by(self.db_subencounter_class.start_time.desc())

        self.subencounter_list.set_result(result)

        if selection != -1:
            self.subencounter_list.SetSelection(selection)
            self.set_subencounter(self.subencounter_list.get_selected_object())
            #self.subencounter_form.set_object(self.subencounter_list.get_selected_object())
        else:
            self.subencounter_form.Hide()

        self.changed = False
        self._update_toolbar()
