"""
SQLalchemy database schema for auto mo.
"""
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Integer, String, ForeignKey, Boolean
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
    sex = Column(String(1))
    bed_no = Column(String(5))
    diagnosis = Column(String(250))
    rxs = relationship("Rx", back_populates="patient", cascade="all, delete, delete-orphan")
    active = Column(Boolean)


class Rx(Base):
    patient_id = Column(Integer, ForeignKey('patient.id'))
    patient = relationship("Patient", back_populates="rxs")
    drug_name = Column(String(250))
    drug_order = Column(String(250))
    active = Column(Boolean)


class Drug(Base):
    name = Column(String(250))


class Diagnosis(Base):
    name = Column(String(250))


class Doctor(Base):
    name = Column(String(250))


class Preset(Base):
    name = Column(String(250))
    rxs = relationship("PresetRx", back_populates="preset", cascade="all, delete, delete-orphan")


class PresetRx(Base):
    preset_id = Column(Integer, ForeignKey('preset.id'))
    preset = relationship("Preset", back_populates="rxs")
    drug_name = Column(String(250))
    drug_order = Column(String(250))
    active = Column(Boolean)


def StartEngine(uri, echo):
    engine = create_engine(uri, echo=echo)

    Base.metadata.create_all(engine)

    Session.configure(bind=engine)
