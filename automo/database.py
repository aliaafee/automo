"""SQLalchemy database schema for auto mo."""
import datetime

from sqlalchemy import Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Integer, String, ForeignKey, Boolean, Date, Text, DateTime, Float
from sqlalchemy.types import Enum
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref

import config


Session = sessionmaker()


class Base(object):
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    #id = Column(Integer, primary_key=True)


Base = declarative_base(cls=Base)


class Icd10Modifier(Base):
    """Icd10 Modifiers of classes"""
    code = Column(String(10), primary_key=True)

    name = Column(String(250))

    text = Column(Text())
    note = Column(Text())
    classes = relationship("Icd10ModifierClass")


class Icd10ModifierClass(Base):
    """Icd10 Individual Modifier Codes"""
    code = Column(String(20), primary_key=True)

    code_short = Column(String(10))

    preferred = Column(String(250))
    definition = Column(Text())
    inclusion = Column(Text())
    exclusion = Column(Text())

    modifier_code = Column(String(10), ForeignKey('icd10modifier.code'))
    modifier = relationship("Icd10Modifier", back_populates="classes")


class Icd10Class(Base):
    """Icd10 chapters, blocks and categories as a tree structure"""
    code = Column(String(10), primary_key=True)

    kind = Column(Enum("chapter", "block", "category"))

    preferred_plain = Column(String(250))

    preferred = Column(String(250))
    preferred_long = Column(Text())
    inclusion = Column(Text())
    exclusion = Column(Text())
    text = Column(Text())
    note = Column(Text())
    coding_hint = Column(Text())

    usage = Column(Enum("dagger", "aster"), name="usage")

    modifier_code = Column(String(10), ForeignKey('icd10modifier.code'))
    modifier = relationship("Icd10Modifier", foreign_keys=[modifier_code])

    modifier_extra_code = Column(String(10), ForeignKey('icd10modifier.code'))
    modifier_extra = relationship("Icd10Modifier", foreign_keys=[modifier_extra_code])

    parent_code = Column(String(10), ForeignKey("icd10class.code"))
    children = relationship('Icd10Class',
                            backref=backref("parent", remote_side='Icd10Class.code'))

    chapter_code = Column(String(10))
    parent_block_code = Column(String(10))

    problems = relationship("Problem", back_populates="icd10class")


class Patient(Base):
    """Patient patient demographic data and list of problems and encounters of the patient.
      Each patient also has single prescription of medications that have been adviced for the
      patient."""
    id = Column(Integer, primary_key=True)

    hospital_no = Column(String(10))
    national_id_no = Column(String(10))
    name = Column(String(250))
    date_of_birth = Column(Date())
    date_of_death = Column(Date())
    sex = Column(String(1))

    problems = relationship("Problem", back_populates="patient",
                            cascade="all, delete, delete-orphan")

    encounters = relationship("Encounter", back_populates="patient",
                              cascade="all, delete, delete-orphan")

    prescription = relationship("Prescription", back_populates="patient",
                                cascade="all, delete, delete-orphan")

    active = Column(Boolean)

    def age(self):
        """Calculate and return age of patient using date of birth, returns age as string
          with units y, m and d"""
        if self.date_of_birth is not None:
            if self.date_of_death is None:
                return config.format_duration(
                    self.date_of_birth, datetime.date.today()
                )
            else:
                return "died at {0}".format(
                    config.format_duration(self.date_of_birth, self.date_of_death)
                )
        else:
            return "unknown"


class Bed(Base):
    """Bed in the clinic/hospital, each bed is associated with a HospitalStay,
      and a list of previous admissions in the bed."""
    id = Column(Integer, primary_key=True)

    number = Column(String(250))

    ward_id = Column(Integer, ForeignKey('ward.id'))
    ward = relationship("Ward", back_populates="beds")

    encounter = relationship("HospitalStay", uselist=False, back_populates="bed",
                             foreign_keys="HospitalStay.bed_id")
    previous_encounters = relationship("HospitalStay", back_populates="discharged_bed",
                                       foreign_keys="HospitalStay.discharged_bed_id")

    def __repr__(self):
        if self.ward is None:
            return self.number
        return "{0} {1}".format(self.ward.bed_prefix, self.number)


class Ward(Base):
    """Ward in the clinic/hospital, each ward has multiple beds"""
    id = Column(Integer, primary_key=True)

    name = Column(String(250))
    bed_prefix = Column(String(250))

    beds = relationship("Bed", back_populates="ward")

    def __repr__(self):
        return self.name


class Problem_Encounter(Base):
    """This object links problems and encounter"""
    id = Column(Integer, primary_key=True)

    problem_id = Column(Integer, ForeignKey("problem.id"))#, primary_key=True)
    problem = relationship("Problem", backref=backref("problem_encounter", cascade="all, delete-orphan" ))

    encounter_id = Column(Integer, ForeignKey("encounter.id"))#, primary_key=True)
    encounter = relationship("Encounter", backref=backref("problem_encounter", cascade="all, delete-orphan" ))


class Problem(Base):
    """The problem that the patient has, each problem has an icd10 code with relevant 
      modifiers, each problem can have multiple encounters. A problem has a start_date.
      Chronic problems eg: Hypertension do not have and end date. But acute problems that
      have resolved with no/minimal residual effects have an end date. For example Acute 
      Appendicites which has been operated on and patient had come for follow up and all 
      symptoms resolved can have the problem made inactive by entering an end date.

      TODO: Consider making the problems into a tree structure, eg: Dabetes Mellitus as
      root problem and child problem like Diabetic foot infections etc..."""
    id = Column(Integer, primary_key=True)

    patient_id = Column(Integer, ForeignKey('patient.id'))
    patient = relationship("Patient", back_populates="problems")

    date_start = Column(Date())
    date_end = Column(Date())

    encounters = relationship("Encounter", secondary="problem_encounter")

    icd10class_code = Column(String(10), ForeignKey('icd10class.code'))
    icd10class = relationship("Icd10Class")

    icd10modifier_class_code = Column(String(20), ForeignKey('icd10modifierclass.code'))
    icd10modifier_class = relationship("Icd10ModifierClass",
                                       foreign_keys=[icd10modifier_class_code])

    icd10modifier_extra_class_code = Column(String(20), ForeignKey('icd10modifierclass.code'))
    icd10modifier_extra_class = relationship("Icd10ModifierClass",
                                             foreign_keys=[icd10modifier_extra_class_code])
    def add_encounter(self, encounter):
        """Add an encounter to the problem"""
        self.problem_encounter.append(
            Problem_Encounter(encounter=encounter,problem=self)
        )


class Encounter(Base):
    """The encounter that the patient had with health facility, each encounter
      can be for single or multiple problems. the encounter object can be polymorphic,
      eg: HospitalStay and ClinicVisit are child classes. Possiblity of expanding
      to include other kinds of encounters, and these child encounters can be extended
      furture with more child classes.
      Each encounter instance can have multiple child encounter instances, for example
      a HospitalStay encounter instance can have a SurgicalProcedure as a child encounter
      instance.
      Each encounter has a start time and end time, and is associated with a doctor, and 
      multiple notes."""
    id = Column(Integer, primary_key=True)

    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity':'encounter',
        'polymorphic_on':type
    }

    parent_id = Column(Integer, ForeignKey("encounter.id"))
    children = relationship('Encounter',
                            backref=backref("parent", remote_side='Encounter.id'))

    patient_id = Column(Integer, ForeignKey('patient.id'))
    patient = relationship("Patient", back_populates="encounters")

    start_time = Column(DateTime())
    end_time = Column(DateTime())

    #doctor_id = Column(Integer, ForeignKey('doctor.id'))
    #doctor = relationship("Doctor", back_populates="encounters")

    personnel_id = Column(Integer, ForeignKey('personnel.id'))
    personnel = relationship("Personnel", back_populates="encounters")

    problems = relationship("Problem", secondary="problem_encounter")

    notes = relationship("Note", back_populates="encounter",
                            cascade="all, delete, delete-orphan")

    def add_problem(self, problem):
        """Add a problem to the encounter"""
        self.problem_encounter.append(
            Problem_Encounter(encounter=self,problem=problem)
        )

    def add_child_encounter(self, encounter):
        """Add a child encounter"""
        self.children.append(encounter)


class HospitalStay(Encounter):
    """Hospital Stay Encounter. Each hospital stay is associated with a bed, when the
      patient is discharged after the hospital stay, the bed attribute is cleared and the bed
      number is moved to the discharged_bed attribute."""
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'hospitalstay',
    }

    bed_id = Column(Integer, ForeignKey('bed.id'))
    bed = relationship("Bed", foreign_keys=[bed_id], back_populates="encounter")

    discharged_bed_id = Column(Integer, ForeignKey('bed.id'))
    discharged_bed = relationship("Bed", foreign_keys=[discharged_bed_id],
                                  back_populates="previous_encounters")


class ClinicVisit(Encounter):
    """Clinic Visit Encounter"""
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'clinicvisit',
    }

    room = Column(String(50))


class VitalSigns(Encounter):
    """Record Vital Signs.
      pulse_rate in beats per minute,
      respiratory_rate in breaths per minute,
      diastolic_bp and systolic_bp in mmHg, this is NIBP,
      temperature in degrees Celcius"""
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'vitalsigns',
    }

    pulse_rate = Column(Float)
    respiratory_rate = Column(Float)
    diastolic_bp = Column(Float)
    systolic_bp = Column(Float)
    temperature = Column(Float)


class VitalSignsExtended(VitalSigns):
    """Record extended vital signs. extended VitalSigns with more variables
      in addition to signs in VitalSigns.
      cvp (central venous pressure) in mmHg 
      systolic_ibp and diastolic_ibp in mmHg
      cap_spo2 in % (capillary spo2)"""
    id = Column(Integer, ForeignKey('vitalsigns.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity':'vitalsignsextended'
    }

    cvp = Column(Float)
    systolic_ibp = Column(Float)
    diastolic_ibp = Column(Float)
    cap_spo2 = Column(Float)


class SurgicalProcedure(Encounter):
    """Surgical Procedure.
      The post operative diagnosis will be the problems associated with this
      encounter. Preoperative diagnosis will written in uncoded text form. The encounter
      start time will be the time the patient is induced and the encounter time is the time
      patient is transferred to recovery room. The main operating surgeon will be the doctor
      for the encounter. """
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'surgicalprocedure'
    }

    preoperative_diagnosis = Column(Text())

    procedure_name = Column(Text())

    findings = Column(Text())


class Note(Base):
    """The patient encounter notes. Parent class of all notes, 
      there are multiple child classes, eg: Patient History,
      Progress notes, Examination notes. Can be extended with more
      child classes."""
    id = Column(Integer, primary_key=True)

    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity':'note',
        'polymorphic_on':type
    }

    encounter_id = Column(Integer, ForeignKey('encounter.id'))
    encounter = relationship("Encounter", back_populates="notes")


class History(Note):
    """Patient History Note"""
    id = Column(Integer, ForeignKey('note.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'history',
    }

    chief_complaints = Column(Text())
    presenting_illness = Column(Text())
    past = Column(Text())


class Progress(Note):
    """Patient Progress Notes. SOAP format."""
    id = Column(Integer, ForeignKey('note.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'progress',
    }

    subjective = Column(Text())
    objective = Column(Text())
    assesment = Column(Text())
    plan = Column(Text())


class Prescription(Base):
    """Patient Prescription"""
    id = Column(Integer, primary_key=True)

    patient_id = Column(Integer, ForeignKey('patient.id'))
    patient = relationship("Patient", back_populates="prescription")

    date_from = Column(Date())
    date_to = Column(Date())

    started_by_id = Column(Integer, ForeignKey('doctor.id'))
    started_by = relationship("Doctor", foreign_keys=[started_by_id],
                              back_populates="started_medications")

    stopped_by_id = Column(Integer, ForeignKey('doctor.id'))
    stopped_by = relationship("Doctor", foreign_keys=[stopped_by_id],
                              back_populates="stopped_medications")

    drug_id = Column(Integer, ForeignKey('drug.id'))
    drug = relationship("Drug")
    drug_order = Column(String(250))
    active = Column(Boolean)


class Drug(Base):
    """Drugs"""
    id = Column(Integer, primary_key=True)

    name = Column(String(250))

    def __repr__(self):
        return self.name


class Personnel(Base):
    """Health Facility Personnel"""
    id = Column(Integer, primary_key=True)

    type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity':'personnel',
        'polymorphic_on':type
    }

    record_card_no = Column(String(250))
    name = Column(String(250))

    encounters = relationship("Encounter", back_populates="personnel")


class Doctor(Personnel):
    """Doctors, has list of encounters doctor had with patient."""
    id = Column(Integer, ForeignKey('personnel.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'doctor',
    }

    pmr_no = Column(String(250))

    started_medications = relationship("Prescription", back_populates="started_by",
                                       foreign_keys="Prescription.started_by_id")
    stopped_medications = relationship("Prescription", back_populates="stopped_by",
                                       foreign_keys="Prescription.stopped_by_id")

    def __repr__(self):
        return "{0} ({1})".format(self.name, self.pmr_no)


class Nurse(Personnel):
    """Nurses
      TODO: Record administered drugs."""
    id = Column(Integer, ForeignKey('personnel.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'nurse',
    }

    pnr_no = Column(String(250))

    def __repr__(self):
        return "{0} ({1})".format(self.name, self.pnr_no)


class PresetPrescription(Base):
    """Preset Drug Regimens"""
    id = Column(Integer, primary_key=True)

    name = Column(String(250))

    medications = relationship("PresetMedication", back_populates="preset", cascade="all, delete, delete-orphan")


class PresetMedication(Base):
    """Medication order in a drug regimen, duration is in days"""
    id = Column(Integer, primary_key=True)

    preset_id = Column(Integer, ForeignKey('presetprescription.id'))
    preset = relationship("PresetPrescription", back_populates="medications")

    drug_id = Column(Integer, ForeignKey('drug.id'))
    drug = relationship("Drug")

    drug_order = Column(String(250))
    duration = Column(Integer) #In Days

    active = Column(Boolean)


def StartEngine(uri, echo, client_version):
    """Initializes the database Engine and creates tables as needed.
      TODO: Check that client_version matches the database version"""

    engine = create_engine(uri, echo=echo)

    Base.metadata.create_all(engine)

    Session.configure(bind=engine)


def main():
    """DB testing. Populates the database with test data."""
    from _version import __version__
    from sqlalchemy.orm import exc

    uri = "sqlite:///wardpresc-data.db"
    StartEngine(uri, False, __version__)

    session = Session()

    def add_unique(table, id=1, **kwds):
        try:
            row = session.query(table).filter(table.id == id).one()
        except exc.NoResultFound:
            row = table(**kwds)
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
        id=1,
        hospital_no="1231",
        national_id_no="A123456",
        name="Ali Aafee",
        date_of_birth=datetime.date(1940,10,2),
        sex="M"
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

    prob = add_unique(
        Problem,
        patient=p,
        icd10class_code="A00"
    )

    enc = add_unique(
        HospitalStay,
        id=1,
        patient=p,
        personnel=doc,
        start_time=datetime.datetime(2017,3,4,10,55,00)
    )

    if len(enc.problems) == 0:
        enc.add_problem(prob)
        session.commit()

    enc = add_unique(
        ClinicVisit,
        id=2,
        patient=p
    )

    if len(enc.problems) == 0:
        enc.add_problem(prob)
        session.commit()

    import code; code.interact(local=dict(globals(), **locals()))


if __name__ == '__main__':
    main()