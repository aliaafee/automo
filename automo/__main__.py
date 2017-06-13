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
    from database import *

    print "Testing Database"
    session = database.Session()

    print "Add Ward"
    sw_ward = database.Ward(
        name="Surgical Ward",
        bed_prefix="SW"
    )
    session.add(sw_ward)
    session.commit()

    print "Add beds"
    for x in range(10):
        new_bed = database.Bed(
            ward_id=sw_ward.id,
            number=x + 1
        )
        session.add(new_bed)
    session.commit()

    print "Add doctor"
    doc = database.Doctor(
        name="Dr. Ali Aafee",
        pmr_no="PMR-001"
    )
    session.add(doc)
    session.commit()

    print "Add drugs"
    drg = database.Drug(name="Ceftriaxone 1g")
    session.add(drg)
    session.commit()
    drg = database.Drug(name="Metronidazole 500mg")
    session.add(drg)
    session.commit()

    print "Add dxs"
    """
    new_dx = database.Icd10Category(id="A00.0", name="Cholera")
    session.add(new_dx)
    new_dx = database.Icd10Category(id="A02.1", name="Salmonella sepsis")
    session.add(new_dx)
    """

    print "Add Patient"
    new_pt = database.Patient(
        name="Ali Aafee",
        age="30",
        sex="M"
    )
    session.add(new_pt)
    session.commit()
    print new_pt.id

    import datetime
    pre_admission = database.Admission(
        patient_id=new_pt.id,
        discharged_bed_id=2,
        admitted_date=datetime.date(2017, 5, 8),
        discharged_date=datetime.date(2017, 5, 18),
        admission_notes="Pain abdomen x 10 days",
        admitting_doctor_id=1
    )
    session.add(pre_admission)
    session.commit()
    pre_admission_diagnosis = database.Diagnosis(
        admission_id=pre_admission.id,
        icd10class_code="A00.0",
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
    new_admission_diagnosis = database.Diagnosis(
        admission_id=new_admission.id,
        icd10class_code="A02.1",
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
