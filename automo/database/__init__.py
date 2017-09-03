"""SQLalchemy database schema for Auto MO
  Classes should be imported from this, and not from individual
  module files"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from .base import Base
from .icd10 import Icd10Modifier, Icd10ModifierClass, Icd10Class
from .patient import Patient
from .address import Address
from .bed import Bed
from .ward import Ward
from .problem_encounter import problem_encounter_association_table
from .problem import Problem
from .encounters import Encounter,\
                        Admission,\
                        ClinicVisit,\
                        Measurements,\
                        VitalSigns,\
                        VitalSignsExtended,\
                        SurgicalProcedure
from .notes import Note,\
                   History,\
                   Progress
from .prescription import Prescription
from .drug import Drug
from .personnel import Personnel,\
                       Doctor,\
                       Nurse
from .preset_prescription import PresetMedication, PresetPrescription


Session = sessionmaker()

def StartEngine(uri, echo, client_version):
    """Initializes the database Engine and creates tables as needed.
      TODO: Check that client_version matches the database version"""

    engine = create_engine(uri, echo=echo)

    Base.metadata.create_all(engine)

    Session.configure(bind=engine)



if __name__ == '__main__':
    main()