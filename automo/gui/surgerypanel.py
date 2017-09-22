"""Surgical Procedures Panel"""
import wx

from .. import database as db
from .. import config
from . import images
from .encounternotebookpage import EncounterNotebookPage
from .dbqueryresultbox import DbQueryResultBox
from .dbform import DbFormPanel, DbDateField, DbStringField, DbMultilineStringField, DbRelationField

class SurgeryPanel(EncounterNotebookPage):
    """Surgical Procedures Notebook Page"""
    def __init__(self, parent, session, **kwds):
        super(SurgeryPanel, self).__init__(parent, session, **kwds)

        splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self.surgery_list = DbQueryResultBox(splitter, self._surgery_decorator)

        fields = [
            DbDateField("Time Started", 'start_time', required=True),
            DbDateField("Time Completed", 'end_time', required=True),
            DbRelationField("Surgeon", 'personnel', self.session.query(db.Doctor)),
            DbStringField("Preop Diagnosis", 'preoperative_diagnosis'),
            DbStringField("Postop Diagnosis", 'postoperative_diagnosis'),
            DbStringField("Precedure Name", 'procedure_name'),
            DbMultilineStringField("Findings", 'findings'),
            DbMultilineStringField("Steps", 'steps'),
        ]

        self.left_panel = wx.Panel(splitter, style=wx.BORDER_THEME)
        self.surgery_form = DbFormPanel(self.left_panel, db.SurgicalProcedure, fields, scrollable=False)
        sizer = wx.BoxSizer()
        sizer.Add(self.surgery_form, 1, wx.EXPAND | wx.ALL, border=5)
        self.left_panel.SetSizer(sizer)

        splitter.SplitVertically(self.surgery_list, self.left_panel, 200)

        self.surgery_form.Hide()

        self.surgery_list.Bind(wx.EVT_LISTBOX, self._on_encounter_selected)

        self.toolbar.AddLabelTool(wx.ID_ADD, "Add", images.get("add"), wx.NullBitmap, wx.ITEM_NORMAL, "Add", "")
        self.toolbar.Bind(wx.EVT_TOOL, self._on_add, id=wx.ID_ADD)
        self.toolbar.Realize()

        self.sizer.Add(splitter, 1, wx.EXPAND | wx.ALL, border=5)


    def _surgery_decorator(self, encounter_object, query_string):
        date_str = config.format_date(encounter_object.start_time)
        html = u'<font size="2"><table width="100%">'\
                    '<tr>'\
                        '<td>Surgery <b>{0}</b></td>'\
                    '</tr>'\
                    '<tr>'\
                        '<td><ul><li>{1}</li></ul></td>'\
                    '</tr>'\
                '</table></font>'

        return html.format(date_str, encounter_object.procedure_name)


    def _on_add(self, event):
        pass


    def _on_encounter_selected(self, event):
        surgery = self.surgery_list.get_selected_object()

        if surgery is None:
            self.surgery_form.Hide()
            return

        self.surgery_form.Show()
        self.surgery_form.set_object(surgery)

        self.left_panel.Layout()


    def set_encounter(self, encounter):
        super(SurgeryPanel, self).set_encounter(encounter)

        result = self.session.query(db.SurgicalProcedure)\
                    .filter(db.SurgicalProcedure.parent == self.encounter)\
                    .order_by(db.ClinicalEncounter.start_time.desc())
        
        print result.count()

        self.surgery_list.set_result(result)
        self.surgery_form.Hide()


