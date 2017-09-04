"""Batch import patients"""
import csv
import wx
import wx.grid

from .. import config
from .. import database as db
from .dbcombobox import DbComboBox

COL_INT = 0
COL_STR = 1
COL_AGE = 2
COL_SEX = 3
COL_BED = 4


class BatchPatientImporter(wx.Dialog):
    """Dialog to import a group of patients from tab delimated file/clipboard"""
    def __init__(self, parent, session, **kwds):
        super(BatchPatientImporter, self).__init__(
             parent, style=wx.CLOSE_BOX | wx.RESIZE_BORDER | wx.SYSTEM_MENU | wx.CAPTION,
            **kwds)
        self.session = session

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

        self.cmd_paste = wx.Button(self, label="Paste")
        self.cmd_paste.Bind(wx.EVT_BUTTON, self._on_paste)

        self.cmd_save = wx.Button(self, label="Import and Admit")
        self.cmd_save.Bind(wx.EVT_BUTTON, self._on_save)

        self.cmb_doctor = DbComboBox(self, self.session)
        self.cmb_doctor.set_items(self.session.query(db.Doctor).all())

        self.cmb_ward = DbComboBox(self, self.session)
        self.cmb_ward.set_items(self.session.query(db.Ward).all())

        self.patient_grid = wx.grid.Grid(self)
        self._setup_grid()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.cmb_doctor, 0, wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.cmb_ward, 0, wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.cmd_paste, 0, wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.patient_grid, 1, wx.EXPAND | wx.ALL, border=5)
        sizer.Add(self.cmd_save, 0, wx.EXPAND | wx.ALL, border=5)
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

        text = """A123456	400001	Circum One	1y	M	10	1
A123457	400002	Circum Two	3y	M	12	2
A123458	400003	Circum Three	1y8m	M	13	3
A123459	400004	Circum Four	2y4m	M	15	4
A123460	400005	Circum Five	8y	M	13	5
A123461	400006	Circum Six	4y	M	14	6
A123462	400007	Circum Seven	6y	M	17	7
A123463	400008	Circum Eight	4y	M	18	8
A123464	400009	Circum Nine	5y	M	19	9
A123465	400010	Circum Ten	3y	M	20	10
A123466	400011	Circum Eleven	5y	M	10	11
A123467	400012	Circum Twelve	6y	M	11	12
A123468	400013	Circum Thirteen	7y	M	12	13
A123469	400014	Circum Fourteen	8y	M	13	14"""

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

            if self._add_patients(admitting_doctor, ward):
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
        return isvalid


    def _add_patients(self, admitting_doctor, ward):
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
                measurement.start_time = admission.start_time
                measurement.end_time = admission.start_time
                admission.add_child_encounter(measurement)
            self.session.commit()
            return True
        except ValueError:
            self.session.rollback()
            return False
