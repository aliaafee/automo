"""Generate blank database
  Run this file from project root, generates database and places it
  in test/test_dbs/blank.db"""

import sys
from datetime import datetime, date

sys.path.append("./")

from automo._version import __version__
from automo import database as db
from automo import icd10claml

def generate():
    db.StartEngine("sqlite:///test/test_dbs/blank.db", False, __version__)
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
        description = "Life-threatening complication (including CNS complications)* requiring IC/ICU-management. Single organ dysfunction."
    )
    session.add(grade)

    grade = db.ComplicationGrade(
        id = "IVb",
        description = "Life-threatening complication (including CNS complications)* requiring IC/ICU-management. Multiorgan dysfunction."
    )
    session.add(grade)

    grade = db.ComplicationGrade(
        id = "V",
        description = "Death of patient"
    )
    session.add(grade)


    session.commit()


if __name__ == "__main__":
    generate()