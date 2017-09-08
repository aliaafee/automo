"""Automo Test Suite"""
import sys
import tempfile
import unittest
import shutil

import datetime
from dateutil.relativedelta import relativedelta

sys.path.append("./")

from automo._version import __version__
from automo import database as db
from automo import config


class ConfigTest(unittest.TestCase):
    def test_parse_duration(self):
        #Parse integer as years
        self.assertEqual(config.parse_duration("12"), relativedelta(years=12))

        #Parse _y string
        self.assertEqual(config.parse_duration("12y"), relativedelta(years=12))

        #Parse _m string
        self.assertEqual(config.parse_duration("3m"), relativedelta(months=3))

        #Parse _d string
        self.assertEqual(config.parse_duration("3d"), relativedelta(days=3))

        #Parse _y _m _d string
        self.assertEqual(config.parse_duration("1y 2m 3d"),
                         relativedelta(years=1, months=2, days=3))

        #Parse _d _y _m string
        self.assertEqual(config.parse_duration("3d 1y 2m "),
                         relativedelta(years=1, months=2, days=3))

        #Parse multi year months
        self.assertEqual(config.parse_duration("19m"),
                         relativedelta(years=1, months=7))

        #Parse noisy string
        self.assertEqual(config.parse_duration("3y asfk 2m asfkawf 1d"),
                         relativedelta(years=3, months=2, days=1))

        #Parse invalid thing
        with self.assertRaises(ValueError):
            config.parse_duration("xyamgd")
        with self.assertRaises(ValueError):
            config.parse_duration("1 years 3 months")




class BaseTest(unittest.TestCase):
    def setUp(self):
        db_file = tempfile.mktemp(".db")
        #print "Temp test db at {}".format(db_file)
        shutil.copyfile("test/test_dbs/test.db", db_file)
        db_uri = "sqlite:///{}".format(db_file)

        db.StartEngine(db_uri, False, __version__)
        self.session = db.Session()

        self.test_patient = db.Patient(name="Test Patient")
        self.session.add(self.test_patient)
        self.session.commit()

        self.patients = self.session.query(db.Patient).all()
        self.beds = self.session.query(db.Bed).all()
        self.doctors = self.session.query(db.Doctor).all()
        self.nurses = self.session.query(db.Nurse).all()




class PatientTest(BaseTest):
    def test_create_patient(self):
        self.assertEqual("Test Patient", self.test_patient.name)


    def test_set_age(self):
        self.patients[0].set_age(relativedelta(years=37), today=datetime.date(2017,1,1))
        self.assertEqual(datetime.date(1980,1,1), self.patients[0].date_of_birth)


    def test_admit(self):
        self.patients[0].admit(self.session, self.doctors[0], self.beds[0])
        self.session.commit()

        #See if admission successful
        self.assertEqual(self.beds[0], self.patients[0].encounters[-1].bed)

        #Try to admit an already admitted patient
        with self.assertRaises(db.dbexception.AutoMODatabaseError):
            self.patients[0].admit(self.session, self.doctors[0], self.beds[1])

        #Try to admit another patient in an occupied bed
        with self.assertRaises(db.dbexception.AutoMODatabaseError):
            self.patients[1].admit(self.session, self.doctors[0], self.beds[0])

        self.patients[0].discharge(self.session)
        self.session.commit()

        #Is discharge successful
        self.assertEqual(None, self.patients[0].get_current_encounter(self.session))

        #Try to discharge a discharged patient
        with self.assertRaises(db.dbexception.AutoMODatabaseError):
            self.patients[0].discharge(self.session)

        self.patients[0].admit(self.session, self.doctors[0], self.beds[1])
        self.session.commit()

        #Readmission succesful?
        self.assertEqual(self.beds[1], self.patients[0].encounters[-1].bed)

        self.patients[0].discharge(self.session)
        self.session.commit()

        #Discharge again succesful?
        self.assertEqual(None, self.patients[0].get_current_encounter(self.session))

        self.patients[0].encounters[0].end_time = None
        self.assertNotEqual(None, self.patients[0].get_current_encounter(self.session))

        self.patients[0].encounters[1].end_time = None

        #Multiple active discharges, (should not happen)
        with self.assertRaises(db.dbexception.AutoMODatabaseError):
            self.patients[0].get_current_encounter(self.session)

        self.patients[0].encounters[0].end()
        self.assertNotEqual(None, self.patients[0].get_current_encounter(self.session))

        self.patients[0].encounters[1].end()
        self.assertEqual(None, self.patients[0].get_current_encounter(self.session))

        self.session.commit()

        #Try to admit patient under personnel that is not doctor
        with self.assertRaises(db.dbexception.AutoMODatabaseError):
            self.patients[0].admit(self.session, self.nurses[0], self.beds[0])




class EncounterTest(BaseTest):
    def test_add_problem(self):
        #Try to add a problem from one patient to another patient, should raise exception
        with self.assertRaises(db.dbexception.AutoMODatabaseError):
            self.patients[0].encounters[0].add_problem(self.patients[1].problems[0])

        #Try to add a problem that has already been added to enounter, should raise exception
        with self.assertRaises(db.dbexception.AutoMODatabaseError):
            self.patients[1].encounters[0].add_problem(
                self.patients[1].problems[0]
            )




class AdmissionTest(BaseTest):
    def test_prescribe_drug(self):
        drugs = self.session.query(db.Drug).all()

        #Prescribe drug by object
        self.patients[0].encounters[0].prescribe_drug(self.session, drugs[0], "", "1 tab OD x 10days")
        self.assertEqual(
            self.patients[0].encounters[0].prescription[0].drug,
            drugs[0]
        )

        #Prescribe drug by string name
        self.patients[0].encounters[0].prescribe_drug(self.session, None, drugs[1].name, "1 tab OD x 10days")
        self.assertEqual(
            self.patients[0].encounters[0].prescription[1].drug,
            drugs[1]
        )

        #Prescribe with name as empty string
        with self.assertRaises(db.dbexception.AutoMODatabaseError):
            self.patients[0].encounters[0].prescribe_drug(self.session, None, "", "1 tab OD x 10days")


        #Prescribe drug by string for drug not in database, it should be added automatically
        self.patients[0].encounters[0].prescribe_drug(self.session, None, "Prodrug", "1 tab OD x 10days")
        drugs = self.session.query(db.Drug).all()
        self.assertEqual(
            drugs[2].name,
            "Prodrug"
        )




class ProblemTest(BaseTest):
    def test_add_encounter(self):
        #Try to add encounter from other patient to problem
        with self.assertRaises(db.dbexception.AutoMODatabaseError):
            self.patients[0].problems[0].add_encounter(self.patients[1].encounters[0])

        #Try to add duplicate encounter to problem
        with self.assertRaises(db.dbexception.AutoMODatabaseError):
            self.patients[0].problems[0].add_encounter(
                self.patients[0].encounters[0]
            )

    def test_remove_problem(self):
        #Try to remove a problem not associated with this encounter
        with self.assertRaises(db.dbexception.AutoMODatabaseError):
            self.patients[1].encounters[1].remove_problem(self.patients[1].problems[1])

        #Remove problem associated with this enounter and also another enounter
        problems_count_before = len(self.patients[1].problems)
        self.patients[1].encounters[1].remove_problem(self.patients[1].problems[0])
        problems_count_after = len(self.patients[1].problems)
        self.assertEqual(problems_count_before, problems_count_after)

        #Remove problem not associated with any other encounter, should remove the
        #problem from patient also
        problems_count_before = len(self.patients[1].problems)
        self.patients[1].encounters[2].remove_problem(self.patients[1].problems[1])
        problems_count_after = len(self.patients[1].problems)
        self.assertEqual(problems_count_before, problems_count_after + 1)






if __name__ == "__main__":
    unittest.main()