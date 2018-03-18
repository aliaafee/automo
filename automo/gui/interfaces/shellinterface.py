"""AutoMO Python Shell"""
from dateutil.relativedelta import relativedelta as duration
from datetime import datetime, date
import wx
import wx.py

from ... import database as db
from ..icd10coder import Icd10Coder
from .baseinterface import BaseInterface


class ShellInterface(BaseInterface):
    """Python Shell for AutoMO"""
    def __init__(self, parent, session=None):
        super(ShellInterface, self).__init__(parent, session)

        self.set_title("Python Shell")

        self.shell = wx.py.shell.Shell(self)

        patients = self.session.query(db.Patient)
        beds = self.session.query(db.Bed)
        doctors = self.session.query(db.Doctor)
        nurses = self.session.query(db.Nurse)
        def create_ward(name, bed_prefix, bed_count):
            ward = db.Ward()
            ward.name = name
            ward.bed_prefix = bed_prefix
            self.session.add(ward)
            for bed_number in range(1, bed_count+1):
                new_bed = db.Bed()
                new_bed.number = unicode(bed_number)
                ward.beds.append(new_bed)
            
        self.shell.interp.locals = {
            'patient': patients,
            'bed': beds,
            'doctor' : doctors,
            'nurse' : nurses,
            'session': self.session,
            'query': self.session.query,
            'db': db,
            'quit': self.Close,
            'icd10coder': Icd10Coder,
            'duration' : duration,
            'datetime' : datetime,
            'date' : date,
            'create_ward': create_ward
        }