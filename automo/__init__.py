"""
AutoMO
------

Electronic Medical Record.

Copyright (C) 2017 Ali Aafee
"""

from ._version import __version__
from . import database as db
from . import icd10claml
from . import report

DEFAULT_DB_URI = "sqlite:///patient-data.db"


def start(uri, debug=False):
    """starts db session at the given db uri"""
    db.StartEngine(uri, debug, __version__)


def import_icd10claml(filename, uri, debug=False):
    """Import Icd 10 ClaML file to database"""
    db.StartEngine(uri, debug, __version__)

    session = db.Session()

    print "Importing ClaML from {0}...".format(filename)

    icd10claml.import_to_database(filename, session)

    print "Done import"
