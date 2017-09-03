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
GUI_INTERFACES = ['gui-shell', 'gui-ward']


def app_license():
    """App license"""
    print "Auto MO {0}".format(__version__)
    print "--------------------------------"
    print "Copyright (C) 2017 Ali Aafee"
    print ""


def usage():
    """App usage"""
    app_license()
    print "Usage:"
    print "    -h, --help"
    print "       Displays this help"
    print "    -f, --interface"
    print "       Start with interface, default is 'shell',"
    print "       available interfaces '{}',".format("', '".join(CLI_INTERFACES))
    print "       '{}'".format("', '".join(GUI_INTERFACES))
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


#TO DELELTE
"""
def db_test():
    #test code to check database functionality
    #this will be removed eventually
    from database import *

    print "Testing Database"
    session = Session()

    print "Deleting All Data"
    count = session.query(Ward).delete()
    print count
    count = session.query(Bed).delete()
    print count
    count = session.query(Doctor).delete()
    print count
    count = session.query(Drug).delete()
    print count
    count = session.query(Patient).delete()
    print count
    count = session.query(Admission).delete()
    print count
    count = session.query(Condition).delete()
    print count
    count = session.query(Prescription).delete()
    print count

    print "Add Ward"
    sw_ward = Ward(
        name="Surgical Ward",
        bed_prefix="SW"
    )
    session.add(sw_ward)
    session.commit()

    print "Add beds"
    for x in range(10):
        new_bed = Bed(
            ward_id=sw_ward.id,
            number=x + 1
        )
        session.add(new_bed)
    session.commit()

    print "Add doctor"
    doc = Doctor(
        name="Dr. Adam West",
        pmr_no="PMR-001"
    )
    session.add(doc)
    session.commit()

    print "Add drugs"
    drg = Drug(name="INJ CEFTRIAXONE 1G")
    session.add(drg)
    session.commit()
    drg = Drug(name="INJ METRONIDAZOLE 500MG")
    session.add(drg)
    session.commit()

    print "Add Patient"
    new_pt = Patient(
        hospital_no="1231",
        national_id_no="A046974",
        name="John Adams",
        date_of_birth=datetime.date(1854, 10, 17),
        sex="F"
    )
    session.add(new_pt)
    session.commit()

    print "Add Patient"
    new_pt = Patient(
        hospital_no="1231",
        national_id_no="A124212",
        name="Adam West",
        date_of_birth=datetime.date(1965, 5, 27),
        sex="M"
    )
    session.add(new_pt)
    session.commit()
    print new_pt.id

    import datetime
    pre_admission = Admission(
        patient_id=new_pt.id,
        discharged_bed_id=2,
        admitted_date=datetime.date(2017, 5, 8),
        discharged_date=datetime.date(2017, 5, 18),
        admission_notes="Pain abdomen x 10 days",
        admitting_doctor_id=1
    )
    session.add(pre_admission)
    session.commit()
    pre_admission_diagnosis = database.Condition(
        admission_id=pre_admission.id,
        icd10class_code="K35",
        date=datetime.date(2017, 6, 8)
    )
    session.add(pre_admission_diagnosis)
    session.commit()
    med = database.Prescription(
        date_from=datetime.date(2017, 6, 8),
        date_to=datetime.date(2017, 6, 15),
        admission_id=pre_admission.id,
        drug_id=1,
        drug_order="IV BD x 10 days",
        active=True
    )
    session.add(med)
    session.commit()
    med = database.Prescription(
        date_from=datetime.date(2017, 6, 8),
        date_to=datetime.date(2017, 6, 20),
        admission_id=pre_admission.id,
        drug_id=2,
        drug_order="IV TDS x 10 days",
        active=True
    )
    session.add(med)
    session.commit()

    new_admission = database.Admission(
        patient_id=new_pt.id,
        bed_id=1,
        admitted_date=datetime.date(2017, 6, 8),
        discharged_date=None,
        admission_notes="Pain abdomen x 10 days",
        admitting_doctor_id=1
    )
    session.add(new_admission)
    session.commit()
    new_admission_diagnosis = database.Condition(
        admission_id=new_admission.id,
        icd10class_code="M72.6",
        icd10modifier_class_code="S13M00_57",
        date=datetime.date(2017, 6, 8)
    )
    session.add(new_admission_diagnosis)
    session.commit()
    med = database.DischargeRx(
        admission_id=new_admission.id,
        drug_id=1,
        drug_order="IV BD x 10 days",
        active=True
    )
    session.add(med)
    session.commit()
    med = database.DischargeRx(
        admission_id=new_admission.id,
        drug_id=2,
        drug_order="IV TDS x 10 days",
        active=True
    )
    session.add(med)
    session.commit()

    #p = new_pt
    #app = wx.PySimpleApp(0)
    #from icd10coder import Icd10Coder

    #import code; code.interact(local=dict(globals(), **locals()))

    #exit()
"""
