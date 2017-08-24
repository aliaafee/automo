"""Patient panel"""
import dateutil.relativedelta as rd
import wx

from .. import config
from .. import images
from .. import database as db

from . import events
from .patientinfo import PatientInfoPanelSmall
from .dbqueryresultbox import DbQueryResultBox

#from admissionpanel import AdmissionPanel


class PatientPanel(wx.Panel):
    """Patient Panel"""
    def __init__(self, parent, session, **kwds):
        super(PatientPanel, self).__init__(parent, **kwds)

        self.session = session
        self.patient = None

        #self.toolbar = self._get_toolbar()

        #splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        #self.right_panel = wx.Panel(splitter)
        #right_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        self.patient_info = PatientInfoPanelSmall(self, session)
        #right_panel_sizer.Add(self.patient_info, 0, wx.ALL | wx.EXPAND, border=5)

        #self.lbl_admissions = wx.StaticText(self.right_panel, label="Admissions")
        #right_panel_sizer.Add(self.lbl_admissions, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)

        #self.admissions_list = DbQueryResultBox(self.right_panel, self._admissions_decorator)
        #self.admissions_list.Bind(wx.EVT_LISTBOX, self._on_admission_selected)
        #right_panel_sizer.Add(self.admissions_list, 1, wx.EXPAND | wx.ALL, border=5)
        #self.right_panel.SetSizer(right_panel_sizer)

        self.notebook = wx.Notebook(self)

        self.summary_panel = wx.Panel(self.notebook)
        self.notebook.AddPage(self.summary_panel, "Summary")

        self.demography_panel = wx.Panel(self.notebook)
        self.notebook.AddPage(self.demography_panel, "Demography")

        self.admission_panel = wx.Panel(self.notebook)#AdmissionPanel(splitter, self.session)
        self.admission_panel.Bind(events.EVT_AM_ADMISSION_CHANGED, self._on_admission_changed)
        self.notebook.AddPage(self.admission_panel, "Admissions")

        self.prescription_panel = wx.Panel(self.notebook)
        self.notebook.AddPage(self.prescription_panel, "Prescription")

        self.notes_panel = wx.Panel(self.notebook)
        self.notebook.AddPage(self.notes_panel, "Notes")

        self.graph_panel = wx.Panel(self.notebook)
        self.notebook.AddPage(self.graph_panel, "Graphs")

        def un():
            return False
        def p_set(obj):
            return False
        self.admission_panel.is_unsaved = un
        self.admission_panel.set = p_set
        self.admission_panel.admission = True
        self.admission_panel.editable = True

        #splitter.SplitVertically(self.right_panel, self.admission_panel)
        #splitter.SetMinimumPaneSize(100)
        #splitter.SetSashPosition(250)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        #sizer.Add(self.toolbar, 0, wx.EXPAND | wx.TOP | wx.LEFT, border=5)
        sizer.Add(self.patient_info, 0, wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, border=5)

        self.SetSizer(sizer)
        self.patient_info.Hide()
        self.notebook.Hide()
        #self.lbl_admissions.Hide()
        #self.admissions_list.Hide()

        self.Bind(wx.EVT_WINDOW_DESTROY, self._on_close)


    #def _get_toolbar(self):
    #    self.locked_bmp = images.get("locked_24")
    #    self.unlocked_bmp = images.get("unlocked_24")

    #    toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)

        #toolbar.AddLabelTool(wx.ID_REFRESH, "Refresh", images.get("refresh_24"),
        #                          wx.NullBitmap, wx.ITEM_NORMAL, "Refresh", "")

        #toolbar.AddSeparator()

    #    toolbar.AddLabelTool(wx.ID_PRINT, "Print", images.get("print_24"),
    #                              wx.NullBitmap, wx.ITEM_NORMAL, "Print", "")

    #    toolbar.AddStretchableSpace()

    #    toolbar.AddLabelTool(wx.ID_EDIT, "Lock/Unlock", self.locked_bmp,
    #                              wx.NullBitmap, wx.ITEM_NORMAL, "Lock/Unlock Admission for Editing", "")

        #toolbar.Bind(wx.EVT_TOOL, self._on_refresh, id=wx.ID_REFRESH)
    #    toolbar.Bind(wx.EVT_TOOL, self._on_toggle_admission_editable, id=wx.ID_EDIT)

    #    toolbar.Realize()

    #    toolbar.Hide()

    #    return toolbar


    #def _update_toolbar(self):
    #    if self.admission_panel.admission is not None:
    #        self.toolbar.EnableTool(wx.ID_EDIT, True)
    #        if self.admission_panel.editable:
    #            self.toolbar.SetToolNormalBitmap(wx.ID_EDIT, self.unlocked_bmp)
    #        else:
    #            self.toolbar.SetToolNormalBitmap(wx.ID_EDIT, self.locked_bmp)
    #    else:
    #        self.toolbar.EnableTool(wx.ID_EDIT, False)
    #        self.toolbar.SetToolNormalBitmap(wx.ID_EDIT, self.locked_bmp)


    def _on_close(self, event):
        if self.is_unsaved():
            self.save_changes()
            print "Changes saved on window destroy"


    #def _on_refresh(self, event):
    #    if self.is_unsaved():
    #        self.save_changes()
    #        print "Changes saved"
    #
    #    self.set(self.patient)


    def _on_toggle_admission_editable(self, event):
        if self.admission_panel.editable:
            self.admission_panel.set_editable(False)
        else:
            self.admission_panel.set_editable(True)
        self._update_toolbar()


    def _admissions_decorator(self, admission_object, query_string):
        date_str = ""
        if admission_object.end_time is None:
            date_str += "<b>{0}</b> (current)".format(
                config.format_date(admission_object.start_time)
            )
        else:
            date_str += "<b>{0}</b> ({1})".format(
                config.format_date(admission_object.start_time),
                config.format_duration(
                    rd.relativedelta(
                        admission_object.end_time, admission_object.start_time
                    )
                )
            )

        diagnoses = []
        for problem in admission_object.problems:
            diagnoses.append(problem.icd10class.preferred)
        diagnoses_str = "</li><li>".join(diagnoses)

        html = u'<font size="2"><table width="100%">'\
                    '<tr>'\
                        '<td>{0}</td>'\
                    '</tr>'\
                    '<tr>'\
                        '<td><ul><li>{1}</li></ul></td>'\
                    '</tr>'\
                '</table></font>'

        return html.format(date_str, diagnoses_str)


    def _on_admission_changed(self, event):
        self.admissions_list.RefreshAll()


    def _on_admission_selected(self, event):
        if self.admission_panel.is_unsaved():
            self.admission_panel.save_changes()
            print "Changes saved"

        admission_selected = self.admissions_list.get_selected_object()

        if admission_selected is None:
            self.admission_panel.unset()
            return

        self.admission_panel.set(admission_selected)
        #self._update_toolbar()


    def is_unsaved(self):
        """Check to see if any changes have been saved, must do before closing"""
        if self.patient is None:
            return False

        if self.patient_info.is_unsaved():
            return True

        if self.admission_panel.is_unsaved():
            return True

        return False


    def save_changes(self):
        if self.patient is None:
            return

        if self.patient_info.is_unsaved():
            self.patient_info.save_changes()

        if self.admission_panel.is_unsaved():
            self.admission_panel.save_changes()


    def refresh(self):
        """Refresh Contents of Panel"""
        if self.patient is None:
            return
        
        if self.is_unsaved():
            self.save_changes()
            print "Changes saved"

        self.set(self.patient)


    def unset(self):
        """Unset selected patient"""
        self.patient = None

        #self.toolbar.Hide()

        self.patient_info.unset()

        #self.admissions_list.clear()

        self.patient_info.Hide()
        self.notebook.Hide()
        #self.lbl_admissions.Hide()
        #self.admissions_list.Hide()
        #self.right_panel.Layout()

        #self.admission_panel.unset()


    def set(self, patient):
        """Set selected patient"""
        if patient is None:
            self.unset()
            return

        self.patient = patient

        #self.toolbar.Show()

        self.patient_info.set(self.patient)

        #admissions = self.session.query(db.Admission)\
        #                .filter(db.Admission.patient == self.patient)\
        #                .order_by(db.Admission.start_time.desc())

        #self.admissions_list.set_result(admissions)

        self.patient_info.Show()
        self.notebook.Show()
        #self.lbl_admissions.Show()
        #self.admissions_list.Show()
        #self.right_panel.Layout()

        #admissions_count = self.admissions_list.GetItemCount()
        #if admissions_count > 0:
        #    self.admissions_list.SetSelection(0)
        #    self._on_admission_selected(None)
        #else:
        #    self.admission_panel.unset()

        #self._update_toolbar()
        self.Layout()

        


def main():
    #Testing
    import database
    database.StartEngine("sqlite:///wardpresc-data.db", False, "")
    session = database.Session()
    app = wx.PySimpleApp(0)

    mainFrame = wx.Frame(None, size=(800, 600))

    pnl = PatientPanel(mainFrame, session)

    patient = session.query(database.Patient)\
                .filter(database.Patient.id == 1)\
                .one()

    pnl.set(patient)

    app.SetTopWindow(mainFrame)

    mainFrame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()