"""AutoMO Python Shell"""
from dateutil.relativedelta import relativedelta as duration
from datetime import datetime, date
import wx
import wx.py

from .. import database as db
from .baseinterface import BaseInterface
from .icd10coder import Icd10Coder


class ShellInterface(BaseInterface):
    """Python Shell for AutoMO"""
    def __init__(self, parent, session=None):
        super(ShellInterface, self).__init__(parent, session)

        self.shell = wx.py.shell.Shell(self)

        patients = self.session.query(db.Patient).all()
        beds = self.session.query(db.Bed).all()
        doctors = self.session.query(db.Doctor).all()
        nurses = self.session.query(db.Nurse).all()
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
            'date' : date
        }
