"""Subencounters Page"""
from datetime import datetime
import wx

from ... import config
from .. import events
from .. import images
from .. import dbform as fm
from ..dblistbox import DbListBox
from ..newadmissionwizard.basepage import BasePage


ID_REMOVE = wx.NewId()

class SubencountersPage(BasePage):
    """Subencounters Page"""
    def __init__(self, parent, session, title):
        super(SubencountersPage, self).__init__(parent, session, title)
        self.subencounter = None

        self.subencounters = []

        self.subencounter_classes = {}
        self.subencounter_fields = {}
        self.subencounter_subtitle_decorators = {}
        self.subencounter_list_decorators = {}
        self.subencounter_titles = {}

        self.toolbar = wx.ToolBar(self, style=wx.TB_VERTICAL | wx.TB_NODIVIDER)
        self.toolbar.AddTool(wx.ID_ADD, "Add", images.get("add_24"), wx.NullBitmap, wx.ITEM_NORMAL, "Add", "")
        self.toolbar.AddTool(ID_REMOVE, "Remove", images.get("delete"), wx.NullBitmap, wx.ITEM_NORMAL, "Remove", "")
        self.toolbar.Realize()

        self.toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_remove, id=ID_REMOVE)

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self.subencounter_list = DbListBox(splitter, self._subencounter_list_decorator)
        self.subencounter_list.Bind(wx.EVT_LISTBOX, self._on_subencounter_selected)

        self.subencounter_form = fm.FormSwitcher(splitter, session, style=wx.BORDER_THEME)
        self.subencounter_form.Bind(events.EVT_AM_DB_FORM_CHANGED, self._on_field_changed)

        splitter.SplitVertically(self.subencounter_list, self.subencounter_form, 200)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.toolbar, 0, wx.EXPAND | wx.ALL, border=1)
        hsizer.Add(splitter, 1, wx.EXPAND | wx.ALL, border=1)

        self.sizer.Add(wx.StaticText(self, label=" "), 0, wx.EXPAND | wx.ALL, border=2)
        self.sizer.Add(hsizer, 1, wx.EXPAND | wx.ALL, border=2)

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


    def get_subencounters(self):
        return self.subencounters


    def _add_new_subencounter(self, subencounter_class):
        new_subencounter = subencounter_class()
        new_subencounter.start_time = datetime.now()
        new_subencounter.end_time = new_subencounter.start_time
        self.subencounters.append(new_subencounter)
        self._update_subencounter_list()
        self.subencounter_list.SetSelection(len(self.subencounters) - 1)
        self._set_subencounter(new_subencounter)


    def _on_add_subencounter(self, event):
        new_subencounter_class = self.add_menu_id_subencounter_class[event.GetId()]
        self._add_new_subencounter(new_subencounter_class)


    def _on_add(self, event):
        if len(self.subencounter_classes) == 1:
            new_subencounter_class = self.subencounter_classes.values()[0]
            self._add_new_subencounter(new_subencounter_class)
            return
        self.PopupMenu(self.add_menu)


    def _on_remove(self, event):
        selection = self.subencounter_list.get_selected_object()
        try:
            self.subencounters.remove(selection)
        except ValueError:
            pass
        else:
            self._update_subencounter_list()
            self.subencounter_form.unset_object()


    def _on_subencounter_selected(self, event):
        if self.subencounter is not None:
            self.subencounter_form.update_object(self.subencounter)

        selected = self.subencounter_list.get_selected_object()

        self._set_subencounter(selected)


    def _set_subencounter(self, subencounter):
        self.subencounter = subencounter

        if self.subencounter is None:
            self.subencounter_form.unset_object()
            return

        self.subencounter_form.set_object(
            self.subencounter,
            self.subencounter_fields[subencounter.type]
        )


    def _on_field_changed(self, event):
        if self.subencounter is not None:
            self.subencounter_form.update_object(self.subencounter)
        self.subencounter_list.RefreshAll()


    def _update_subencounter_list(self):
        self.subencounter_list.set_items(self.subencounters)


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

    def _subencounter_list_decorator(self, encounter_object):
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

        return self.subencounter_list_decorators[type_name](encounter_object)
