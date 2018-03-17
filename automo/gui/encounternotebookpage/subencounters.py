"""List with Form View for Subencounters"""
from datetime import datetime
import wx

from ... import config
from ... import database as db
from .. import images
from .. import events
from ..widgets import DbQueryResultBox
from ..dbform import FormSwitcher
from .encounternotebookpage import EncounterNotebookPage


class Subencounters(EncounterNotebookPage):
    """List with Form View for subenounters, all subencounters in one,
      One can add the types of subenounters that are visibles, and the forms."""
    def __init__(self, parent, session, **kwds):
        super(Subencounters, self).__init__(parent, session, **kwds)

        self.subencounter = None

        self.subencounter_classes = {}
        self.subencounter_fields = {}
        self.subencounter_subtitle_decorators = {}
        self.subencounter_list_decorators = {}
        self.subencounter_titles = {}

        self.changed = False

        self.toolbar.AddTool(wx.ID_ADD, "Add", images.get("add"), wx.NullBitmap, wx.ITEM_NORMAL, "Add", "")
        self.toolbar.AddSeparator()
        self.toolbar.AddTool(wx.ID_SAVE, "Save", images.get("save"), wx.NullBitmap, wx.ITEM_NORMAL, "Save changes", "")
        self.toolbar.Realize()

        self.toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_save, id=wx.ID_SAVE)

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self.subencounter_list = DbQueryResultBox(splitter, self.subencounter_list_decorator, style=wx.LB_MULTIPLE)
        self.subencounter_list.Bind(wx.EVT_LISTBOX, self._on_subencounter_selected)
        self.subencounter_list.Bind(wx.EVT_RIGHT_DOWN, self._on_subencounter_context)

        self.subencounter_form = FormSwitcher(splitter, session, style=wx.BORDER_THEME)
        self.subencounter_form.Bind(events.EVT_AM_DB_FORM_CHANGED, self._on_field_changed)

        splitter.SplitVertically(self.subencounter_list, self.subencounter_form, 200)

        self.sizer.Add(splitter, 1, wx.EXPAND | wx.ALL, border=5)

        self.subencounter_menu = wx.Menu()
        self.subencounter_menu.Append(wx.ID_REMOVE, "Remove", "Remove Selected Item.")
        self.subencounter_menu.Bind(wx.EVT_MENU, self._on_remove_subencounter, id=wx.ID_REMOVE)

        self.add_menu_id_subencounter_class = {}
        self.add_menu = wx.Menu()


    def add_subencounter_class(self, title, subencounter_class, subencounter_fields, subtitle_decorator=None, list_decorator=None):
        type_name = subencounter_class().__mapper_args__['polymorphic_identity']

        self.subencounter_classes[type_name] = subencounter_class
        self.subencounter_fields[type_name] = subencounter_fields
        self.subencounter_subtitle_decorators[type_name] = subtitle_decorator
        self.subencounter_list_decorators[type_name] = list_decorator
        self.subencounter_titles[type_name] = title

        add_menu_id = wx.NewId()
        self.add_menu_id_subencounter_class[add_menu_id] = subencounter_class
        self.add_menu.Append(add_menu_id, title, "Add {} item".format(title))
        self.add_menu.Bind(wx.EVT_MENU, self._on_add_subencounter, id=add_menu_id)


    def _default_list_decorator(self, encounter_object, title, subtitle_decorator=None):
        date_str = config.format_date(encounter_object.start_time)
        html = u'<font size="2"><table width="100%">'\
                    '<tr>'\
                        '<td valign="top">&bull;</td>'\
                        '<td valign="top"><b>{0}</b></td>'\
                        '<td valign="top" width="100%"><b>{1}</b></td>'\
                    '</tr>'\
                    '{2}'\
                '</table></font>'

        subtitle = ""
        if subtitle_decorator is not None:
            subtitle_html = u'<tr>'\
                                '<td></td>'\
                                '<td colspan="2">{}</td>'\
                            '</tr>'
            subtitle = subtitle_html.format(subtitle_decorator(encounter_object))

        return html.format(date_str, title, subtitle)


    def subencounter_list_decorator(self, encounter_object, query_string):
        """Decorator of Subencounter List"""
        type_name = encounter_object.type

        if type_name not in self.subencounter_list_decorators.keys():
            return self._default_list_decorator(encounter_object,
                                                self.subencounter_titles[type_name],
                                                self.subencounter_subtitle_decorators[type_name])

        if self.subencounter_list_decorators[type_name] is None:
            return self._default_list_decorator(encounter_object,
                                                self.subencounter_titles[type_name],
                                                self.subencounter_subtitle_decorators[type_name])

        return self.subencounter_list_decorators[type_name](encounter_object, query_string)


    def _on_field_changed(self, event):
        self.changed = True
        self._update_toolbar()

        
    def _on_add(self, event):
        self.PopupMenu(self.add_menu)


    def _on_add_subencounter(self, event):
        if self.encounter is None:
            return

        if self.is_unsaved():
            self.save_changes()

        new_subencounter_class = self.add_menu_id_subencounter_class[event.GetId()]
        new_subencounter = new_subencounter_class()
        new_subencounter.start_time = datetime.now()
        new_subencounter.end_time = new_subencounter.start_time
        self.encounter.add_child_encounter(new_subencounter)
        self.session.commit()
        self.set_encounter(self.encounter)
        self._set_subencounter(new_subencounter)


    def _on_save(self, event):
        self.save_changes()


    def _update_toolbar(self):
        if self.changed:
            self.toolbar.EnableTool(wx.ID_SAVE, True)
        else:
            self.toolbar.EnableTool(wx.ID_SAVE, False)


    def _on_subencounter_context(self, event):
        if not self.editable:
            return

        self.PopupMenu(self.subencounter_menu)
    

    def _on_remove_subencounter(self, event):
        with wx.MessageDialog(self, 'Remove selected item(s)?', 'Remove Item',
                              wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) as dlg:
            dlg.CenterOnParent()
            if dlg.ShowModal() == wx.ID_YES:
                selected = self.subencounter_list.get_all_selected_object()
                for subencounter in selected:
                    self.encounter.remove_child_encounter(subencounter)
                self.session.commit()

                self.set_encounter(self.encounter, preserve_selection=False)


    def is_unsaved(self):
        if self.encounter is not None and self.subencounter is not None:
            if self.changed:
                return True
        return False


    def save_changes(self):
        if self.encounter is not None and self.subencounter is not None:
            self.subencounter_form.update_object(self.subencounter)
            self.session.commit()
            self._set_subencounter(self.subencounter)
            self.subencounter_list.RefreshAll()


    def _on_subencounter_selected(self, event):
        if self.changed:
            self.save_changes()
            
        selected = self.subencounter_list.get_selected_object()

        self._set_subencounter(selected)


    def editable_on(self):
        super(Subencounters, self).editable_on()
        self.subencounter_form.unlock()


    def editable_off(self):
        super(Subencounters, self).editable_off()
        self.subencounter_form.lock()


    def _set_subencounter(self, subencounter):
        self.subencounter = subencounter

        if self.subencounter is None:
            self.subencounter_form.unset_object()
            return

        self.subencounter_form.set_object(self.subencounter,
                                      self.subencounter_fields[subencounter.type])

        self.changed = False
        self._update_toolbar()


    def _unset_subencounter(self):
        self.subencounter = None
        self.subencounter_form.unset_object()


    def set_encounter(self, encounter, preserve_selection=True):
        selection = -1
        if self.encounter is not None and self.encounter == encounter and preserve_selection:
            selection, cookie = self.subencounter_list.GetFirstSelected()

        super(Subencounters, self).set_encounter(encounter)

        result = self.session.query(db.Encounter)\
                    .filter(db.Encounter.parent == self.encounter)\
                    .filter(db.Encounter.type.in_(self.subencounter_classes.keys()))\
                    .order_by(db.Encounter.start_time.desc())

        self.subencounter_list.set_result(result)

        if selection != -1:
            self.subencounter_list.SetSelection(selection)
            self._set_subencounter(self.subencounter_list.get_selected_object())
        else:
            if self.subencounter_list.GetItemCount() > 0:
                self.subencounter_list.SetSelection(0)
                self._set_subencounter(self.subencounter_list.get_selected_object())
            else:
                self._unset_subencounter()


        self.changed = False
        self._update_toolbar()
