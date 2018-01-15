"""Generate test database
  Run this file from project root, generates database and places it
  in test/test_dbs/test.db"""

import sys
from datetime import datetime, date

sys.path.append("./")

from automo._version import __version__
from automo import database as db
from automo import icd10claml

def generate():
    db.StartEngine("sqlite:///test/test_dbs/test.db", False, __version__)
    session = db.Session()

    icd10claml.import_to_database("icd10/icdClaML2016ens.xml", session)

    grade = db.ComplicationGrade(
        id = "0",
        description = "No Complication"
    )
    session.add(grade)

    grade = db.ComplicationGrade(
        id = "I",
        description = "Any deviation from the normal postoperative course without the need for pharmacological treatment or surgical, endoscopic and radiological interventions. Allowed therapeutic regimens are: drugs as antiemetics, antipyretics, analgetics, diuretics and electrolytes and physiotherapy. This grade also includes wound infections opened at the bedside."
    )
    session.add(grade)

    grade = db.ComplicationGrade(
        id = "II",
        description = "Requiring pharmacological treatment with drugs other than such allowed for grade I complications. Blood transfusionsand total parenteral nutritionare also included."
    )
    session.add(grade)

    grade = db.ComplicationGrade(
        id = "IIIa",
        description = "Requiring surgical, endoscopic or radiological intervention NOT under general anesthesia."
    )
    session.add(grade)

    grade = db.ComplicationGrade(
        id = "IIIb",
        description = "Requiring surgical, endoscopic or radiological intervention under general anesthesia."
    )
    session.add(grade)

    grade = db.ComplicationGrade(
        id = "IVa",
        description = "Life-threatening complication (including CNS complications) requiring IC/ICU-management. Single organ dysfunction."
    )
    session.add(grade)

    grade = db.ComplicationGrade(
        id = "IVb",
        description = "Life-threatening complication (including CNS complications) requiring IC/ICU-management. Multiorgan dysfunction."
    )
    session.add(grade)

    grade = db.ComplicationGrade(
        id = "V",
        description = "Death of patient"
    )
    session.add(grade)

    doctor1 = db.Doctor()
    doctor1.record_card_no = "1231"
    doctor1.name = "Dr. One"
    session.add(doctor1)

    doctor2 = db.Doctor()
    doctor2.record_card_no = "1232"
    doctor2.name = "Dr. Two"
    session.add(doctor2)

    doctor3 = db.Doctor()
    doctor3.record_card_no = "1233"
    doctor3.name = "Dr. Three"
    session.add(doctor3)

    nurse1 = db.Nurse()
    nurse1.record_card_no = "1233"
    nurse1.name = "S/N One"
    session.add(nurse1)

    patient1 = db.Patient(name="Patient One")
    patient1.sex = "M"
    patient1.time_of_birth = date(1982, 1, 2)
    patient1.hospital_no = "1231"
    patient1.national_id_no = "A123451"
    session.add(patient1)

    problem1 = db.Problem()
    problem1.icd10class_code = "A01"
    problem1.start_time = datetime(2017, 1, 1, 12, 0)
    session.add(problem1)
    patient1.problems.append(problem1)

    patient2 = db.Patient(name="Patient Two")
    patient2.sex = "F"
    patient2.time_of_birth = date(1972, 1, 2)
    patient2.hospital_no = "1232"
    patient2.national_id_no = "A123452"
    session.add(patient2)

    problem2 = db.Problem()
    problem2.icd10class_code = "A02"
    problem2.start_time = datetime(2017, 2, 1, 11, 0)
    session.add(problem2)
    patient2.problems.append(problem2)

    problem3 = db.Problem()
    problem3.icd10class_code = "B02"
    session.add(problem3)
    patient2.problems.append(problem3)

    patient3 = db.Patient(name="Patient Three")
    patient3.sex = "M"
    patient3.time_of_birth = date(2016, 2, 1)
    patient3.hospital_no = "1233"
    patient3.national_id_no = "A123453"

    problem4 = db.Problem()
    problem4.icd10class_code = "Z41.2"
    problem4.start_time = datetime(2017, 8, 30)
    session.add(problem4)
    patient3.problems.append(problem4)

    ward = db.Ward(name="Test Ward")
    ward.bed_prefix = "TW"
    session.add(ward)

    bed1 = db.Bed(number="1")
    session.add(bed1)
    ward.beds.append(bed1)
    bed2 = db.Bed(number="2")
    session.add(bed2)
    ward.beds.append(bed2)
    bed3 = db.Bed(number="3")
    session.add(bed3)
    ward.beds.append(bed3)

    admission1 = patient1.admit(session, doctor1, bed1, datetime(2017, 1, 1, 12, 0))
    admission1.add_problem(problem1)
    patient1.discharge(session, datetime(2017, 1, 10, 13, 0))

    admission2 = patient1.admit(session, doctor2, bed2, datetime(2017, 3, 3, 9, 0))
    admission2.add_problem(problem1)
    patient1.discharge(session, datetime(2017, 3, 10, 17, 0))

    clinicvisit1 = db.OutpatientEncounter()
    patient1.add_encounter(clinicvisit1)
    clinicvisit1.start_time = datetime(2017, 3, 21, 10, 55)
    clinicvisit1.personnel = doctor1
    clinicvisit1.add_problem(problem1)
    clinicvisit1.end(datetime(2017, 3, 21, 11, 00))

    admission3 = patient2.admit(session, doctor2, bed1, datetime(2017, 2, 1, 11, 0))
    admission3.add_problem(problem2)
    patient2.discharge(session, datetime(2017, 2, 4, 17,0))

    clinicvisit2 = db.OutpatientEncounter()
    patient2.add_encounter(clinicvisit2)
    clinicvisit2.start_time = datetime(2017, 2, 8, 9, 30)
    clinicvisit2.personnel = doctor2
    clinicvisit2.add_problem(problem2)
    clinicvisit2.end(datetime(2017, 2, 8, 9, 35))

    clinicvisit3 = db.OutpatientEncounter()
    patient2.add_encounter(clinicvisit3)
    clinicvisit3.start_time = datetime(2017, 5, 4, 13, 3)
    clinicvisit3.personnel = doctor1
    clinicvisit3.add_problem(problem3)
    clinicvisit3.end(datetime(2017, 5, 4, 13, 6))

    admission4 = patient3.admit(session, doctor2, bed3, datetime(2017, 8, 30, 5, 42))
    admission4.add_problem(problem4)

    drug1 = db.Drug()
    drug1.name = "INJ NEWMED"
    session.add(drug1)

    drug2 = db.Drug()
    drug2.name = "INJ ULTRAMED"
    session.add(drug2)

    session.commit()


if __name__ == "__main__":
    generate()