"""
AutoMO
------

Program to automate the tedious paper work of MOs

Copyright (C) 2017 Ali Aafee
"""
import sys
import getopt
import wx

from _version import __version__
#from mainframe import MainFrame

import database


class MoPresc(wx.App):
    """
    The Main wx App Object
    """
    def __init__(self, parent=None):
        self.main_frame = None
        wx.App.__init__(self, parent)


    def OnInit(self):
        """ Initializes the App """
        self.main_frame = MainFrame(None)
        self.main_frame.Show()
        return True


def app_license():
    """ App license """
    print "Auto MO {0}".format(__version__)
    print "--------------------------------"
    print "Copyright (C) 2017 Ali Aafee"
    print ""


def usage():
    """ App usage """
    app_license()
    print "Usage:"
    print "    -h, --help"
    print "       Displays this help"
    print "    -d, --debug"
    print "       Output database debug data"
    print "    -i, --icd10claml [filename]"
    print "       Import ICD10 Classification from ClaML xml file"


def start(uri, debug):
    """ starts db session at the given db uri """
    database.StartEngine(uri, debug, __version__)

    #this will be removed
    db_test()

    app = MoPresc()

    app.MainLoop()


def import_icd10claml(filename, uri, debug):
    """Import Icd 10 ClaML file to database"""
    database.StartEngine(uri, debug, __version__)

    session = database.Session()

    import icd10claml

    print "Importing ClaML from {0}...".format(filename)

    icd10claml.import_to_database(filename, session)

    print "Done import"


def db_test():
    """ test code to check database functionality """
    """ this will be removed eventually"""
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
        name="Dr. Ali Aafee",
        pmr_no="PMR-001"
    )
    session.add(doc)
    session.commit()

    print "Add drugs"
    drg = Drug(name="Ceftriaxone 1g")
    session.add(drg)
    session.commit()
    drg = Drug(name="Metronidazole 500mg")
    session.add(drg)
    session.commit()

    print "Add Patient"
    new_pt = Patient(
        name="Ali Aafee",
        age="30",
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
    pre_admission_diagnosis = database.MainCondition(
        admission_id=pre_admission.id,
        icd10class_code="K35",
        date=datetime.date(2017, 6, 8)
    )
    session.add(pre_admission_diagnosis)
    session.commit()
    med = database.DailyRx(
        admission_id=pre_admission.id,
        drug_id=1,
        drug_order="IV BD x 10 days",
        active=True
    )
    session.add(med)
    session.commit()
    med = database.DailyRx(
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
    new_admission_diagnosis = database.MainCondition(
        admission_id=new_admission.id,
        icd10class_code="K85.1",
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

    p = new_pt

    import code; code.interact(local=dict(globals(), **locals()))

    exit()


def main(argv):
    """ starts the app, also reads command line arguments """
    database_uri = "sqlite:///wardpresc-data.db"
    debug = False

    try:
        opts, args = getopt.getopt(argv, "hdi:", ["help", "debug", "icd10claml="])
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
        if opt in ("-d", "--debug"):
            debug = True

    start(database_uri, debug)


if __name__ == '__main__':
    main(sys.argv[1:])
