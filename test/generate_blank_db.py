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

    session.commit()


if __name__ == "__main__":
    generate()