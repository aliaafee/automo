"""SQLalchemy database schema for Auto MO
  Classes should be imported from this, and not from individual
  module files"""

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from .base import Base
from .icd10 import Icd10Modifier, Icd10ModifierClass, Icd10Class
from .patient import Patient
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


def main():
    """DB testing. Populates the database with test data."""
    import datetime
    from _version import __version__
    from sqlalchemy.orm import exc

    uri = "sqlite:///wardpresc-data.db"
    StartEngine(uri, False, __version__)

    session = Session()

    def add_unique(table, id=1, **kwds):
        try:
            row = session.query(table).filter(table.id == id).one()
        except exc.NoResultFound:
            row = table(id=id, **kwds)
            session.add(row)
            session.commit()
        return row

    sw_ward = add_unique(
        Ward,
        name="Surgical Ward",
        bed_prefix="SW"
    )

    for x in range(10):
        new_bed = add_unique(
            Bed,
            id=x + 1,
            ward_id=sw_ward.id,
            number=x + 1
        )

    doc = add_unique(
        Doctor,
        name="Dr. Ali Aafee",
        pmr_no="PMR-123"
    )

    p = add_unique(
        Patient,
        id=2,
        hospital_no="1231",
        national_id_no="A123456",
        name="John Snow",
        date_of_birth=datetime.date(1423,10,2),
        sex="M"
    )

    p = add_unique(
        Patient,
        id=3,
        hospital_no="1231",
        national_id_no="A123456",
        name="Baby Boy",
        date_of_birth=datetime.date(2017,1,2),
        sex="M"
    )

    p = add_unique(
        Patient,
        id=1,
        hospital_no="1231",
        national_id_no="A123456",
        name="Ali Aafee",
        date_of_birth=datetime.date(1940,10,2),
        sex="M"
    )

    prob = add_unique(
        Problem,
        id=0,
        patient=p,
        icd10class_code="A00"
    )

    prob = add_unique(
        Problem,
        id=1,
        patient=p,
        icd10class_code="B01"
    )

    enc = add_unique(
        Admission,
        id=1,
        patient=p,
        personnel=doc,
        bed_id=1,
        start_time=datetime.datetime(2017,3,4,10,55,00)
    )

    if len(enc.problems) == 0:
        enc.add_problem(prob)
        session.commit()

    enc = add_unique(
        Admission,
        id=3,
        patient=p,
        personnel=doc,
        bed_id=None,
        discharged_bed_id=3,
        start_time=datetime.datetime(2014,1,4,10,55,00),
        end_time=datetime.datetime(2014,1,14,9,55,00)
    )

    if len(enc.problems) == 0:
        enc.add_problem(prob)
        session.commit()

    enc = add_unique(
        ClinicVisit,
        id=2,
        patient=p,
        start_time=datetime.datetime(2017,5,4,10,0,00),
        end_time=datetime.datetime(2017,5,4,10,15,00)
    )

    if len(enc.problems) == 0:
        enc.add_problem(prob)
        session.commit()

    #import code; code.interact(local=dict(globals(), **locals()))


if __name__ == '__main__':
    main()