"""List with Form View for Subencounters"""
import wx

from . import images
from .. import config
from .dbqueryresultbox import DbQueryResultBox
from .dbform import DbFormPanel
from .encounternotebookpage import EncounterNotebookPage


class EncounterNotebookList(EncounterNotebookPage):
    """List with Form View for Subencounters"""
    def __init__(self, parent, session, db_subencounter_class, fields, **kwds):
        super(EncounterNotebookList, self).__init__(parent, session, **kwds)

        self.fields = fields
        self.db_subencounter_class = db_subencounter_class

        self.toolbar.AddLabelTool(wx.ID_ADD, "Add", images.get("add"), wx.NullBitmap, wx.ITEM_NORMAL, "Add", "")
        self.toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)
        self.toolbar.Realize()

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self.subencounter_list = DbQueryResultBox(splitter, self.subencounter_list_decorator)
        self.subencounter_list.Bind(wx.EVT_LISTBOX, self._on_subencounter_selected)

        self._left_panel = wx.Panel(splitter, style=wx.BORDER_THEME)

        self.subencounter_form = DbFormPanel(self._left_panel, db_subencounter_class, fields, scrollable=False)

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


    def _on_add(self, event):
        pass


    def _on_subencounter_selected(self, event):
        selected = self.subencounter_list.get_selected_object()

        if selected is None:
            self.subencounter_form.Hide()
            return

        self.subencounter_form.Show()
        self.subencounter_form.set_object(selected)

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
            self.subencounter_form.set_object(self.subencounter_list.get_selected_object())
        else:
            self.subencounter_form.Hide()
