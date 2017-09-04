"""
AutoMO
------

Electronic Medical Record.

Copyright (C) 2017 Ali Aafee
"""
import sys
import getopt
import code
from dateutil.relativedelta import relativedelta as duration
from datetime import datetime, date

from ._version import __version__
from . import icd10claml
from . import database as db
from .gui import AutoMOApp

CLI_INTERFACES = ['shell']
GUI_INTERFACES = ['gui-shell', 'gui-ward', 'gui-cward']


def app_license():
    """App license"""
    print "Auto MO {0}".format(__version__)
    print "----------------------------"
    print "Copyright (C) 2017 Ali Aafee"
    print ""


def usage():
    """App usage"""
    app_license()
    print "Usage:"
    print "    -f, --interface (Option is required)"
    print "       Set the interface to start with."
    print "       available interfaces:"
    print '           cli: "{}"'.format('", "'.join(CLI_INTERFACES))
    print '           gui: "{}"'.format('", "'.join(GUI_INTERFACES))
    print "    -h, --help"
    print "       Displays this help"
    print "    -d, --debug"
    print "       Output database debug data"
    print "    -i, --icd10claml [filename]"
    print "       Import ICD10 2016 Classification from ClaML xml file"


def start(uri, debug):
    """starts db session at the given db uri"""
    db.StartEngine(uri, debug, __version__)


def start_gui(uri, interface, debug):
    """start gui interface"""
    start(uri, debug)

    app = AutoMOApp(interface)

    app.MainLoop()


def start_cli(uri, interface, debug):
    """start cli interface"""
    start(uri, debug)

    if interface == 'shell':
        session = db.Session()
        patients = session.query(db.Patient).all()
        beds = session.query(db.Bed).all()
        doctors = session.query(db.Doctor).all()
        nurses = session.query(db.Nurse).all()
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


def import_icd10claml(filename, uri, debug):
    """Import Icd 10 ClaML file to database"""
    db.StartEngine(uri, debug, __version__)

    session = db.Session()

    print "Importing ClaML from {0}...".format(filename)

    icd10claml.import_to_database(filename, session)

    print "Done import"


def main(argv):
    """starts the app, also reads command line arguments"""
    database_uri = "sqlite:///automo-data.db"
    debug = False
    interface = ''

    try:
        opts, args = getopt.getopt(argv, "hdi:f:", ["help", "debug", "icd10claml=", "interface="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit()
        if opt in ("-i", "--icd10claml"):
            import_icd10claml(arg, database_uri, debug)
            sys.exit()
        if opt in ("-f", "--interface"):
            interface = arg
        if opt in ("-d", "--debug"):
            debug = True

    if interface in CLI_INTERFACES:
        start_cli(database_uri, interface, debug)
    elif interface in GUI_INTERFACES:
        start_gui(database_uri, interface, debug)
    else:
        usage()
        sys.exit(2)
