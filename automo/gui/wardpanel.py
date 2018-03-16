"""Ward Panel"""
import string
import tempfile
import wx
import PyPDF2

from .. import config
from .. import database as db

from . import images
from . import events
from .widgets import DbComboBox, DbQueryResultBox
from .pdfviewer import PDFViewer

ID_DISCHARGE_MULTIPLE = wx.NewId()
ID_PRINT_DISCHARGE_MULTIPLE = wx.NewId()
ID_PRINT_PRESCRIPTION_MULTIPLE = wx.NewId()


class WardPanel(wx.Panel):
    """Ward Panel, select ward, and display list of beds"""
    def __init__(self, parent, session, **kwds):
        super(WardPanel, self).__init__(parent, **kwds)

        self.session = session

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)
        self.toolbar.AddTool(ID_DISCHARGE_MULTIPLE, "Discharge Selected", images.get("discharge"), wx.NullBitmap, wx.ITEM_NORMAL, "Discharge Selected Patient(s)", "")
        self.toolbar.AddTool(wx.ID_PRINT, "Print", images.get("print_24"), wx.NullBitmap, wx.ITEM_NORMAL, "Print Selected Patient(s)", "")
        self.toolbar.Realize()

        self.toolbar.Bind(wx.EVT_TOOL, self._on_discharge_multiple, id=ID_DISCHARGE_MULTIPLE)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_print, id=wx.ID_PRINT)

        self.cmb_ward = DbComboBox(self)
        self.cmb_ward.Bind(wx.EVT_COMBOBOX, self._on_change_ward)

        self.beds_list = DbQueryResultBox(self, self._bed_decorator, style=wx.LB_MULTIPLE)
        self.beds_list.Bind(wx.EVT_LISTBOX, self._on_bed_selected)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.toolbar, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        sizer.Add(self.cmb_ward, 0, wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        sizer.Add(self.beds_list, 1, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(sizer)

        self.print_menu = wx.Menu()
        self.print_menu.Append(ID_PRINT_PRESCRIPTION_MULTIPLE, "Precriptions", "Print Prescriptions")
        self.print_menu.Bind(wx.EVT_MENU, self._on_print_multiple_prescription, id=ID_PRINT_PRESCRIPTION_MULTIPLE)

        self.refresh()


    def _on_print(self, event):
        self.PopupMenu(self.print_menu)


    def _on_discharge_multiple(self, event):
        selected_beds = self.beds_list.get_all_selected_object()

        if not selected_beds:
            print "Nothing Selected"
            return

        patients = []
        admissions = []
        str_patients = []
        for bed in selected_beds:
            if bed.admission is not None:
                patient = bed.admission.patient
                admissions.append(bed.admission)
                patients.append(patient)
                str_patients.append("{0}\t{1}\t{2}\t{3}/{4}".format(
                    str(bed),
                    patient.hospital_no,
                    patient.name,
                    config.format_duration(patient.age),
                    patient.sex
                ))

        if not patients:
            print "No Patients in Beds"
            return

        message = 'Discharge selected patients?\n\n{}'.format("\n".join(str_patients))
        with wx.MessageDialog(self, message, 'Discharge Patients',
                              wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) as dlg:
            dlg.CenterOnParent()
            result = dlg.ShowModal()

            if result != wx.ID_YES:
                return

        try:
            for patient in patients:
                patient.discharge(self.session)
        except Exception as e:
            self.session.rollback()
            with wx.MessageDialog(None,
                "Error Occured. {}".format(e.message),
                "Error",
                wx.OK | wx.ICON_EXCLAMATION) as err_dlg:
                err_dlg.ShowModal()
            return
        else:
            self.session.commit()
            self.refresh_all()

        message = 'Print discharge summaries and prescriptions of selected patients?\n\n{}'.format("\n".join(str_patients))
        with wx.MessageDialog(self, message, 'Print Discharge Summaries',
                              wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION) as dlg:
            dlg.CenterOnParent()
            result = dlg.ShowModal()

            if result != wx.ID_YES:
                return

        summaries = PyPDF2.PdfFileMerger()
        prescriptions = PyPDF2.PdfFileMerger()
        for admission in admissions:
            summary = admission.generate_discharge_summary(self.session)
            with open(summary,"rb") as pdf_file:
                summaries.append(pdf_file)

            prescription = admission.get_prescription_pdf(self.session)
            with open(prescription,"rb") as pdf_file:
                prescriptions.append(pdf_file)

        summaries_filename = tempfile.mktemp(".pdf")
        with open(summaries_filename,"wb") as combined_pdf:
            summaries.write(combined_pdf)

        prescriptions_filename = tempfile.mktemp(".pdf")
        with open(prescriptions_filename,"wb") as combined_pdf:
            prescriptions.write(combined_pdf)

        pdf_view = PDFViewer(None, title="Print Preview - Prescriptions")
        pdf_view.viewer.UsePrintDirect = ``False``
        pdf_view.viewer.LoadFile(prescriptions_filename)
        pdf_view.Show()

        pdf_view = PDFViewer(None, title="Print Preview - Discharge Summaries")
        pdf_view.viewer.UsePrintDirect = ``False``
        pdf_view.viewer.LoadFile(summaries_filename)
        pdf_view.Show()


    def _on_print_multiple_prescription(self, event):
        selected_beds = self.beds_list.get_all_selected_object()

        if not selected_beds:
            print "Nothing Selected"
            return

        admissions = []
        for bed in selected_beds:
            if bed.admission is not None:
                admissions.append(bed.admission)

        prescriptions = PyPDF2.PdfFileMerger()
        for admission in admissions:
            prescription = admission.get_prescription_pdf(self.session)
            with open(prescription,"rb") as pdf_file:
                prescriptions.append(pdf_file)

        prescriptions_filename = tempfile.mktemp(".pdf")
        with open(prescriptions_filename,"wb") as combined_pdf:
            prescriptions.write(combined_pdf)

        pdf_view = PDFViewer(None, title="Print Preview - Prescriptions")
        pdf_view.viewer.UsePrintDirect = ``False``
        pdf_view.viewer.LoadFile(prescriptions_filename)
        pdf_view.Show()


    def refresh(self):
        selection = self.cmb_ward.GetSelection()
        self.cmb_ward.set_items(
            self.session.query(db.Ward).all()
        )   
        if selection != wx.NOT_FOUND:
            self.cmb_ward.SetSelection(selection)
        else:
            self.cmb_ward.SetSelection(0)

        self._on_change_ward(None)

        self.beds_list.RefreshAll()


    def refresh_selected(self):
        self.beds_list.RefreshSelected()


    def refresh_all(self):
        self.beds_list.RefreshAll()


    def _on_bed_selected(self, event):
        selected_bed = self.beds_list.get_selected_object()

        try:
            selected_patient = selected_bed.admission.patient
        except AttributeError:
            selected_patient = None

        event = events.PatientSelectedEvent(events.ID_PATIENT_SELECTED, object=selected_patient)
        wx.PostEvent(self, event)


    def _on_change_ward(self, event):
        selected_ward = self.cmb_ward.get_selected_item()

        if selected_ward is None:
            self.beds_list.clear()
        else:
            query_result = self.session.query(db.Bed)\
                                .filter(db.Bed.ward_id == selected_ward.id)
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
                self._non_breaking(config.format_duration(bed.admission.patient.age)),
                bed.admission.patient.sex
            )
