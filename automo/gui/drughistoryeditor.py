"""Drug History Editor"""
import wx

from .. import database as db
from . import images
from . import events
from .dbqueryresultgrid import DbQueryResultGrid, GridColumnString


class DrugHistoryEditor(wx.Panel):
    """Drug History Editor"""
    def __init__(self, parent, session, **kwds):
        super(DrugHistoryEditor, self).__init__(parent, **kwds)

        self.session = session

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)
        self.toolbar.AddTool(wx.ID_REPLACE, "Merge", images.get("merge_24"), wx.NullBitmap, wx.ITEM_NORMAL, "Merge", "")
        self.toolbar.Bind(wx.EVT_TOOL, self._on_merge, id=wx.ID_REPLACE)
        self.toolbar.Realize()

        self.txt_search = wx.TextCtrl(self)
        self.txt_search.Bind(wx.EVT_TEXT, self._on_change_filter)

        self.drug_grid = DbQueryResultGrid(self, self.session)
        self.drug_grid.add_column(GridColumnString("Drug", 'name', width=400))
        self.drug_grid.HideColLabels()
        self.drug_grid.SetRowLabelSize(40)
        self.drug_grid.Bind(events.EVT_AM_DB_GRID_CELL_CHANGED, self._on_grid_changed)
        query = self.session.query(db.Drug)

        self.drug_grid.set_result(query)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolbar, 0, wx.EXPAND)
        sizer.Add(self.txt_search, 0, wx.TOP | wx.RIGHT | wx.LEFT | wx.EXPAND, border=5)
        sizer.Add(self.drug_grid, 1, wx.ALL | wx.EXPAND, border=5)
        self.SetSizer(sizer)



    def _on_grid_changed(self, event):
        pass


    def _on_merge(self, event):
        drugs = self.drug_grid.get_selected_row_objects()
        
        if len(drugs) < 2:
            return

        drug_strs = ["   {}".format(drug.name) for drug in drugs]

        message = u"Combine:\n{0}\n\nwith\n{1}?".format('\n'.join(drug_strs[1:]), drug_strs[0])

        with wx.MessageDialog(self, message, style=wx.CENTRE | wx.YES_NO) as dlg:
            if dlg.ShowModal() != wx.ID_YES:
                return

        drugs[0].merge_with(self.session, drugs[1:])
        self.session.commit()
        self._on_change_filter(event)


    def _on_change_filter(self, event):
        str_filter = self.txt_search.GetValue()

        query = self.session.query(db.Drug)

        if str_filter != "":
            query = query.filter(db.Drug.name.like("%{}%".format(str_filter)))

        self.drug_grid.set_result(query)

