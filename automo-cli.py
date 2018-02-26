"""AutoMO Command Line Interface"""
import sys
import getopt
import code
from datetime import datetime, date
from dateutil.relativedelta import relativedelta as duration

import automo
from automo import database as db

INTERFACES = ['shell']


def app_license():
    """App license"""
    print "Auto MO {0}".format(automo.__version__)
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
    print '           cli: "{}"'.format('", "'.join(INTERFACES))
    print "    -h, --help"
    print "       Displays this help"
    print "    -d, --debug"
    print "       Output database debug data"
    print "    -i, --icd10claml [filename]"
    print "       Import ICD10 2016 Classification from ClaML xml file"


def start_cli(uri, interface, debug):
    """start cli interface"""
    automo.start(uri, debug)

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


def main(argv):
    """starts the app, also reads command line arguments"""
    database_uri = automo.DEFAULT_DB_URI
    debug = False
    interface = 'shell'

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
            automo.import_icd10claml(arg, database_uri, debug)
            sys.exit()
        if opt in ("-f", "--interface"):
            interface = arg
        if opt in ("-d", "--debug"):
            debug = True

    if interface in automo.CLI_INTERFACES:
        start_cli(database_uri, interface, debug)
    else:
        usage()
        sys.exit(2)


if __name__ == '__main__':
    main(sys.argv[1:])
