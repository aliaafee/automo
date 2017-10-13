"""Batch import patients"""
import datetime
import csv
import wx
import wx.grid

from .. import config
from .. import database as db
from . import images
from .dbcombobox import DbComboBox

COL_INT = 0
COL_STR = 1
COL_AGE = 2
COL_SEX = 3
COL_BED = 4


class BatchPatientImporter(wx.Dialog):
    """Dialog to import a group of patients from tab delimated file/clipboard"""
    def __init__(self, parent, session, size=wx.Size(1000, 600), **kwds):
        super(BatchPatientImporter, self).__init__(
             parent, style=wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION,
             size=size, **kwds)
        self.SetTitle("Batch Patient Importer")
        
        self.session = session

        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)

        self.toolbar.AddTool(wx.ID_PASTE, "Paste", images.get("paste"), wx.NullBitmap, wx.ITEM_NORMAL, "Paste List", "")
        self.toolbar.AddSeparator()
        self.toolbar.AddTool(wx.ID_ADD, "Insert Row", images.get("add"), wx.NullBitmap, wx.ITEM_NORMAL, "Insert Row", "")
        self.toolbar.AddTool(wx.ID_DELETE, "Delete Row", images.get("remove"), wx.NullBitmap, wx.ITEM_NORMAL, "Delete Row", "")
        self.toolbar.Realize()
        self.toolbar.Bind(wx.EVT_TOOL, self._on_paste, id=wx.ID_PASTE)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_row_insert, id=wx.ID_ADD)
        self.toolbar.Bind(wx.EVT_TOOL, self._on_row_delete, id=wx.ID_DELETE)

        self.col_definition = [
            ("ID Number", COL_STR),
            ("Hospital Number", COL_STR),
            ("Name", COL_STR),
            ("Age", COL_AGE),
            ("Sex", COL_SEX),
            ("Weight", COL_INT),
            ("Bed Number", COL_BED)
        ]
        self.col_count = len(self.col_definition)
        self.validation_errors = []

        #self.cmd_paste = wx.Button(self, label="Paste")
        #self.cmd_paste.Bind(wx.EVT_BUTTON, self._on_paste)

        self.cmd_save = wx.Button(self, label="Import and Admit")
        self.cmd_save.Bind(wx.EVT_BUTTON, self._on_save)

        self.cmd_cancel = wx.Button(self, label="Cancel")
        self.cmd_cancel.Bind(wx.EVT_BUTTON, self._on_cancel)

        self.lbl_doctor = wx.StaticText(self, label="Admitting Doctor")
        self.cmb_doctor = DbComboBox(self, self.session, size=(200, -1))
        self.cmb_doctor.set_items(self.session.query(db.Doctor).all())

        self.lbl_ward = wx.StaticText(self, label="Ward")
        self.cmb_ward = DbComboBox(self, self.session, size=(200, -1))
        self.cmb_ward.set_items(self.session.query(db.Ward).all())

        self.patient_grid = wx.grid.Grid(self)
        self._setup_grid()

        foot_sizer = wx.BoxSizer(wx.VERTICAL)
        foot_sizer.Add(self.lbl_doctor, 0 , wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        foot_sizer.Add(self.cmb_doctor, 0 , wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, border=5)
        foot_sizer.Add(self.lbl_ward, 0 , wx.EXPAND | wx.TOP | wx.RIGHT | wx.LEFT, border=5)
        foot_sizer.Add(self.cmb_ward, 0 , wx.EXPAND | wx.BOTTOM | wx.RIGHT | wx.LEFT, border=5)
        #foot_sizer.Add(self.cmd_paste, 0 , wx.EXPAND | wx.ALL, border=5)
        foot_sizer.AddStretchSpacer()
        foot_sizer.Add(self.cmd_save, 0 , wx.EXPAND | wx.ALL, border=5)
        foot_sizer.Add(self.cmd_cancel, 0 , wx.EXPAND | wx.ALL, border=5)

        hsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer.Add(self.toolbar, 0, wx.EXPAND | wx.BOTTOM, border=5)
        hsizer.Add(self.patient_grid, 1, wx.EXPAND)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(hsizer, 1, wx.EXPAND | wx.ALL, border=5)
        sizer.Add(foot_sizer, 0, wx.EXPAND | wx.ALL, border=5)
        self.SetSizer(sizer)


    def _setup_grid(self):
        self.patient_grid.CreateGrid(1, self.col_count)
        for col, definition in enumerate(self.col_definition):
            self.patient_grid.SetColLabelValue(col, definition[0])
        

    def _get_clipboard_text(self):
        if not wx.TheClipboard.IsOpened():  # may crash, otherwise
            do = wx.TextDataObject()
            wx.TheClipboard.Open()
            success = wx.TheClipboard.GetData(do)
            wx.TheClipboard.Close()
            if success:
                return do.GetText()
            else:
                return None


    def _on_paste(self, event):
        text = self._get_clipboard_text()

        if text is None:
            return

        patient_list = self._parse_list(text)

        self.patient_grid.ClearGrid()
        self.patient_grid.DeleteRows(0, self.patient_grid.GetNumberRows())
        self.patient_grid.AppendRows(len(patient_list))

        for row, patient in enumerate(patient_list):
            for col, value in enumerate(patient):
                if col < self.col_count:
                    self.patient_grid.SetCellValue(row, col, value)


    def _on_row_insert(self, event):
        current_row = self.patient_grid.GetGridCursorRow()
        self.patient_grid.InsertRows(current_row, 1)


    def _on_row_delete(self, event):
        selected_rows = self.patient_grid.GetSelectedRows()
        if selected_rows:
            self.patient_grid.DeleteRows(selected_rows[0])


    def _on_cancel(self, event):
        self.EndModal(wx.ID_CANCEL)


    def _on_save(self, event):
        admitting_doctor = self.cmb_doctor.get_selected_item()
        if admitting_doctor is None:
            print "Select doctor"
            return
    
        ward = self.cmb_ward.get_selected_item()
        if ward is None:
            print "Select ward"
            return

        if self._list_isvalid():
            print "List seems ok"

            if self._add_patients(admitting_doctor):
                self.EndModal(wx.ID_OK)
            else:
                print "Error occured while adding patients"
        else:
            print "List not ok, fix the red cells"
            print "\r\n".join(self.validation_errors)
        self.patient_grid.Refresh()


    def _parse_list(self, list_str):
        result = []
        for line in csv.reader(list_str.split('\n'), delimiter='\t'):
            result.append(line)
        return result


    def _cell_isvalid(self, row, col):
        data_type = self.col_definition[col][1]
        col_value = self.patient_grid.GetCellValue(row, col)
        if data_type == COL_INT:
            try:
                value = int(col_value)
                return True
            except ValueError:
                self.validation_errors.append(
                    "In row {0}, col {1}, Invalid integer".format(row, col)
                )
                return False
        elif data_type == COL_STR:
            try:
                value = unicode(col_value)
                if value == "":
                    self.validation_errors.append(
                        "In row {0}, col {1}, Invalid string value".format(row, col)
                    )
                    return False
                return True
            except ValueError:
                self.validation_errors.append(
                    "In row {0}, col {1}, Invalid string value".format(row, col)
                )
                return False
        elif data_type == COL_AGE:
            try:
                value = config.parse_duration(col_value)
                return True
            except ValueError:
                self.validation_errors.append(
                    "In row {0}, col {1}, Invalid format for age, should be _y _m _d".format(row, col)
                )
                return False
        elif data_type == COL_SEX:
            if col_value == "M" or col_value == "F":
                return True
            self.validation_errors.append(
                "In row {0}, col {1}, Invalid format for sex, should be M, F".format(row, col)
            )
            return False
        elif data_type == COL_BED:
            try:
                bed_number = unicode(int(col_value))
                ward = self.cmb_ward.get_selected_item()
                bed_query = self.session.query(db.Bed)\
                                .filter(db.Bed.ward == ward)\
                                .filter(db.Bed.number == bed_number)
                if bed_query.count() != 1:
                    self.validation_errors.append(
                        "In row {0}, col {1}, Bed {2} was not found".format(row, col, bed_number)
                    )
                    return False
                bed = bed_query.one()
                if bed.admission is None:
                    return True
                else:
                    self.validation_errors.append(
                        "In row {0}, col {1}, Bed {2} is already occupied".format(row, col, bed)
                    )
                    return False
            except ValueError:
                self.validation_errors.append(
                    "In row {0}, col {1}, Bed number is not valid".format(row, col)
                )
                return False


    def _get_cell_value(self, row, col):
        data_type = self.col_definition[col][1]
        col_value = self.patient_grid.GetCellValue(row, col)
        if data_type == COL_INT:
            return int(col_value)
        elif data_type == COL_STR:
            return unicode(col_value)
        elif data_type == COL_AGE:
            return config.parse_duration(col_value)
        elif data_type == COL_SEX:
            return unicode(col_value)
        elif data_type == COL_BED:
            bed_number = unicode(int(col_value))
            ward = self.cmb_ward.get_selected_item()
            bed_query = self.session.query(db.Bed)\
                            .filter(db.Bed.ward == ward)\
                            .filter(db.Bed.number == bed_number)
            bed = bed_query.one()
            return bed
            

    def _list_isvalid(self):
        isvalid = True
        self.validation_errors = []
        for row in range(0, self.patient_grid.GetNumberRows()):
            row_isvalid = True
            for col in range(0, self.patient_grid.GetNumberCols()):
                if self._cell_isvalid(row, col):
                    #print "[{0}, {1}] - {2}".format(row, col, self._get_cell_value(row, col))
                    self.patient_grid.SetCellBackgroundColour(row, col, wx.Colour(255, 255, 255))
                else:
                    print "[{0}, {1}] - invalid - {2}".format(row, col, self.patient_grid.GetCellValue(row, col))
                    self.patient_grid.SetCellBackgroundColour(row, col, wx.Colour(255, 0, 0))
                    isvalid = False
                    row_isvalid = False
            if row_isvalid:
                #Check if similar patient exist in database
                id_number = self._get_cell_value(row, 0)
                #hospital_no = self._get_cell_value(row, 1)
                patients = self.session.query(db.Patient)\
                                .filter(db.Patient.national_id_no == id_number)
                if patients.count() > 0:
                    self.patient_grid.SetCellBackgroundColour(row, 0, wx.Colour(255, 0, 0))
                    isvalid = False
                    self.validation_errors.append(
                        "In row {0}, A patient with the same Nation ID number found in database.".format(row)
                    )
        #TODO: Look for duplicates in this list
        return isvalid


    def _add_patients(self, admitting_doctor):
        try:
            patients = []

            for row in range(0, self.patient_grid.GetNumberRows()):
                new_patient = db.Patient()
                new_patient.national_id_no = self._get_cell_value(row, 0)
                new_patient.hospital_no = self._get_cell_value(row, 1)
                new_patient.name = self._get_cell_value(row, 2)
                new_patient.age = self._get_cell_value(row, 3)
                new_patient.sex = self._get_cell_value(row, 4)
                patients.append(new_patient)
                self.session.add(new_patient)

                bed = self._get_cell_value(row, 6)
                
                admission = new_patient.admit(self.session, admitting_doctor, bed)
                
                problem = db.Problem()
                problem.icd10class_code = "Z41.2"
                problem.start_time = admission.start_time
                new_patient.problems.append(problem)
                admission.add_problem(problem)
                
                measurement = db.Measurements()
                measurement.weight = self._get_cell_value(row, 5)
                measurement.record_time = admission.start_time
                admission.add_child_encounter(measurement)

                surgery = db.SurgicalProcedure()
                surgery.personnel = admission.personnel
                surgery.start_time = admission.start_time + datetime.timedelta(days=1)
                surgery.preoperative_diagnosis = "Circumcision"
                surgery.postoperative_diagnosis = "Circumcision"
                surgery.procedure_name = "Circumcision"
                surgery.findings = ""
                surgery.steps = ""
                admission.add_child_encounter(surgery)

                #cefixime_dose = self.cefixime_dose(new_patient.age_td, measurement.weight)
                #if cefixime_dose is not None:
                #    cefixime_order_str = "{}ML PO BD x 5DAYS".format(cefixime_dose)
                admission.prescribe_drug(self.session, None, "SYP CEFO-L", "")

                #paracetamol_dose = self.paracetamol_dose(new_patient.age_td, measurement.weight)
                #if paracetamol_dose is not None:
                #    paracetamol_order_str = "{}ML PO TDS x 5DAYS".format(paracetamol_dose)
                admission.prescribe_drug(self.session, None, "SYP PARACETAMOL", "")
                
            self.session.commit()
            return True
        except ValueError:
            self.session.rollback()
            return False
