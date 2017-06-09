"""
SQLalchemy database schema for auto mo.
"""
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Integer, String, ForeignKey, Boolean, Date, Text
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


Session = sessionmaker()


class Base(object):
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=Base)


class Patient(Base):
    hospital_no = Column(String(10))
    national_id_no = Column(String(10))
    name = Column(String(250))
    age = Column(String(250))
    date_of_birth = Column(Date())
    sex = Column(String(1))
    admissions = relationship("Admission", back_populates="patient",
                              cascade="all, delete, delete-orphan")
    #bed_no = Column(String(5))
    #diagnosis = Column(String(250))
    #rxs = relationship("Rx", back_populates="patient", cascade="all, delete, delete-orphan")
    active = Column(Boolean)


class Admission(Base):
    patient_id = Column(Integer, ForeignKey('patient.id'))
    patient = relationship("Patient", back_populates="admissions")

    bed_id = Column(Integer, ForeignKey('bed.id'))
    bed = relationship("Bed", back_populates="admission")

    discharged_bed_id = Column(Integer)

    admitted_date = Column(Date())
    discharged_date = Column(Date())

    admitting_doctor_id = Column(Integer, ForeignKey('doctor.id'))
    admitting_doctor = relationship("Doctor", back_populates="admissions")

    diagnoses = relationship("AdmissionDiagnosis")

    admission_notes = Column(Text())
    progress_notes = Column(Text())
    discharge_advice = Column(Text())

    daily_rxs = relationship("DailyRx")

    discharge_rxs = relationship("DischargeRx")


class Bed(Base):
    name = Column(String(250))
    admission = relationship("Admission", uselist=False, back_populates="bed")


class AdmissionDiagnosis(Base):
    admission_id = Column(Integer, ForeignKey('admission.id'))

    diagnosis_id = Column(Integer, ForeignKey('diagnosis.id'))
    diagnosis = relationship("Diagnosis")

    date = Column(Date())

    comment = Column(Text())


class Diagnosis(Base):
    icd_code = Column(String(250))
    name = Column(String(250))


class DischargeRx(Base):
    admission_id = Column(Integer, ForeignKey('admission.id'))
    #admission = relationship("Admission", back_populates="discharge_rxs")
    drug_id = Column(Integer, ForeignKey('drug.id'))
    drug = relationship("Drug")
    drug_order = Column(String(250))
    active = Column(Boolean)


class DailyRx(Base):
    admission_id = Column(Integer, ForeignKey('admission.id'))
    #admission = relationship("Admission", back_populates="daily_rxs")
    drug_id = Column(Integer, ForeignKey('drug.id'))
    drug = relationship("Drug")
    drug_order = Column(String(250))
    active = Column(Boolean)


class Drug(Base):
    name = Column(String(250))


class Doctor(Base):
    name = Column(String(250))
    pmr_no = Column(String(250))
    admissions = relationship("Admission", back_populates="admitting_doctor")


class Preset(Base):
    name = Column(String(250))
    rxs = relationship("PresetRx", back_populates="preset", cascade="all, delete, delete-orphan")


class PresetRx(Base):
    preset_id = Column(Integer, ForeignKey('preset.id'))
    preset = relationship("Preset", back_populates="rxs")

    drug_id = Column(Integer, ForeignKey('drug.id'))
    drug = relationship("Drug")

    drug_order = Column(String(250))
    active = Column(Boolean)


def StartEngine(uri, echo, client_version):
    """
    Initializes the database Engine and creates tables
    as needed.
    TODO: Check that client_version matches the database version
    """

    engine = create_engine(uri, echo=echo)

    Base.metadata.create_all(engine)

    Session.configure(bind=engine)
