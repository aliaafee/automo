"""
AutoMO
------

Electronic Medical Record.

Copyright (C) 2017 Ali Aafee
"""
import sys
import code
from datetime import datetime, date
from dateutil.relativedelta import relativedelta as duration

from ._version import __version__
from . import icd10claml
from . import database as db
from . import gui

DEFAULT_DB_URI = "sqlite:///patient-data.db"

CLI_INTERFACES = ['shell']
GUI_INTERFACES = ['gui-shell', 'gui-ward', 'gui-cward']


def start(uri, debug):
    """starts db session at the given db uri"""
    db.StartEngine(uri, debug, __version__)


def start_gui(uri):
    """start gui interface"""
    start(uri, False)

    app = gui.AutoMOApp()

    app.MainLoop()


def start_cli(uri, interface, debug):
    """start cli interface"""
    start(uri, debug)

    if interface == 'shell':
        session = db.Session()
        patients = session.query(db.Patient)
        beds = session.query(db.Bed)
        doctors = session.query(db.Doctor)
        nurses = session.query(db.Nurse)
        shell_locals = {
            'patient': patients,
            'bed': beds,
            'doctor' : doctors,
            'nurse' : nurses,
            'session': session,
            'query': session.query,
            'db': db,
            'quit': sys.exit,
            'duration' : duration,
            'datetime' : datetime,
            'date' : date
        }
        code.interact(local=shell_locals)
    else:
        print "Interface '{}' is not available".format(interface)


def import_icd10claml(filename, uri, debug=False):
    """Import Icd 10 ClaML file to database"""
    db.StartEngine(uri, debug, __version__)

    session = db.Session()

    print "Importing ClaML from {0}...".format(filename)

    icd10claml.import_to_database(filename, session)

    print "Done import"
