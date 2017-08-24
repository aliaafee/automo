"""AutoMO Python Shell"""
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
        self.shell.interp.locals = {
            'p': patients,
            'beds': beds,
            'session': self.session,
            'query': self.session.query,
            'db': db,
            'quit': self.Close,
            'icd10coder': Icd10Coder 
        }
