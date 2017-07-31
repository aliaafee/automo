"""Ward Panel"""
import string
import wx

from events import PatientChangedEvent
from database import Ward, Bed
from dbcombobox import DbComboBox
from dbqueryresultbox import DbQueryResultBox


class WardPanel(wx.Panel):
    """Ward Panel, select ward, and display list of beds"""
    def __init__(self, parent, session, **kwds):
        super(WardPanel, self).__init__(parent, **kwds)

        self.session = session

        self.cmb_ward = DbComboBox(self, self.session)
        self.cmb_ward.Bind(wx.EVT_COMBOBOX, self._on_change_ward)

        self.beds_list = DbQueryResultBox(self, self._bed_decorator)
        self.beds_list.Bind(wx.EVT_LISTBOX, self._on_bed_selected)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.cmb_ward, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        sizer.Add(self.beds_list, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(sizer)

        self.refresh()


    def refresh(self):
        selection = self.cmb_ward.GetSelection()
        self.cmb_ward.set_items(
            self.session.query(Ward).all()
        )   
        if selection != wx.NOT_FOUND:
            self.cmb_ward.SetSelection(selection)

        self.beds_list.RefreshAll()


    def _on_bed_selected(self, event):
        selected_bed = self.beds_list.get_selected_object()
        if selected_bed is None:
            return
        if selected_bed.admission is None:
            return
        if selected_bed.admission.patient is None:
            return

        event = PatientChangedEvent(object=selected_bed.admission.patient)
        wx.PostEvent(self, event)


    def _on_change_ward(self, event):
        selected_ward = self.cmb_ward.get_selected_item()

        if selected_ward is None:
            self.beds_list.clear()
        else:
            query_result = self.session.query(Bed)\
                                .filter(Bed.ward_id == selected_ward.id)
            self.beds_list.set_result(query_result)


    def _non_breaking(self, text):
        return string.replace(text, " ", "&nbsp;")


    def _bed_decorator(self, bed, query_string):
        if bed.admission is None:
            html = '<font size="2">'\
                        '<table width="100%">'\
                            '<tr>'\
                                '<td valign="top" width="40">{0}</td>'\
                                '<td valign="top">'\
                                '<font color="gray">(vacant)</font></font>'\
                                '</td>'\
                            '</tr>'\
                        '</table>'\
                    '</font>'
            return html.format(str(bed))
        else:
            html = '<font size="2">'\
                        '<table width="100%">'\
                            '<tr>'\
                                '<td valign="top" width="40">{0}</td>'\
                                '<td valign="top" width="40">{1}</td>'\
                                '<td valign="top" width="100%">{2}</td>'\
                                '<td valign="top">{3}/{4}</td>'\
                            '</tr>'\
                        '</table>'\
                    '</font>'
            return html.format(
                self._non_breaking(str(bed)),
                bed.admission.patient.hospital_no,
                bed.admission.patient.name,
                self._non_breaking(bed.admission.patient.age()),
                bed.admission.patient.sex
            )
