"""SQLalchemy database schema for Auto MO
  Classes should be imported from this, and not from individual
  module files"""

import sqlalchemy.exc
from sqlalchemy.orm import sessionmaker, configure_mappers
from sqlalchemy import create_engine
#from sqlalchemy_continuum import make_versioned

from .user import UserPlugin

#make_versioned(plugins=[UserPlugin()])

from .base import Base
from .user import User
from .icd10 import Icd10Modifier, Icd10ModifierClass, Icd10Class
from .patient import Patient
from .address import Address
from .bed import Bed
from .ward import Ward
from .problem_encounter import problem_encounter_association_table
from .problem import Problem
from .encounters import Encounter,\
                        ClinicalEncounter,\
                        Admission,\
                        CircumcisionAdmission,\
                        OutpatientEncounter,\
                        Measurements,\
                        VitalSigns,\
                        VitalSignsExtended,\
                        Progress,\
                        SurgicalProcedure,\
                        Investigation,\
                        Imaging,\
                        Endoscopy,\
                        Histopathology,\
                        OtherReport,\
                        CompleteBloodCount,\
                        RenalFunctionTest,\
                        LiverFunctionTest,\
                        OtherEncounter
from .complicationgrade import ComplicationGrade
from .notes import Note,\
                   History
from .prescription import Prescription
from .drug import Drug
from .personnel import Personnel,\
                       Doctor,\
                       Nurse
from .preset_prescription import PresetMedication, PresetPrescription

#configure_mappers()

Session = sessionmaker()


def dirty_upgrade(engine):
    try:
        engine.execute("SELECT active FROM personnel")
    except sqlalchemy.exc.OperationalError:
        print "Creating Personnel Active Column"
        engine.execute("ALTER TABLE personnel ADD COLUMN active BOOLEAN;")

    try:
        engine.execute("SELECT active FROM ward")
    except sqlalchemy.exc.OperationalError:
        print "Creating Ward Active Column"
        engine.execute("ALTER TABLE ward ADD COLUMN active BOOLEAN;")


def StartEngine(uri, echo, client_version):
    """Initializes the database Engine and creates tables as needed.
      TODO: Check that client_version matches the database version"""

    engine = create_engine(uri, echo=echo)

    Base.metadata.create_all(engine)

    #Dirty Upgrade
    dirty_upgrade(engine)

    Session.configure(bind=engine)
