"""
SQLalchemy database schema for auto mo.
"""
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Integer, String, ForeignKey, Boolean, Date, Text
from sqlalchemy.types import Enum
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref


Session = sessionmaker()


class Base(object):
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    #id = Column(Integer, primary_key=True)


Base = declarative_base(cls=Base)


class Icd10Modifier(Base):
    code = Column(String(10), primary_key=True)

    name = Column(String(250))

    text = Column(Text())
    note = Column(Text())
    classes = relationship("Icd10ModifierClass")


class Icd10ModifierClass(Base):
    code = Column(String(20), primary_key=True)

    code_short = Column(String(10))

    preferred = Column(String(250))
    definition = Column(Text())
    inclusion = Column(Text())
    exclusion = Column(Text())

    modifier_code = Column(String(10), ForeignKey('icd10modifier.code'))
    modifier = relationship("Icd10Modifier", back_populates="classes")


class Icd10Class(Base):
    code = Column(String(10), primary_key=True)

    kind = Column(Enum("chapter", "block", "category"))

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

    #exclude_modifer_codes = Column(String(250))

    parent_code = Column(String(10), ForeignKey("icd10class.code"))
    children = relationship('Icd10Class',
                            backref=backref("parent", remote_side='Icd10Class.code'))

    chapter_code = Column(String(10))

    main_conditions = relationship("MainCondition", back_populates="icd10class")
    other_conditions = relationship("OtherCondition", back_populates="icd10class")


class Patient(Base):
    id = Column(Integer, primary_key=True)

    hospital_no = Column(String(10))
    national_id_no = Column(String(10))
    name = Column(String(250))
    age = Column(String(250))
    date_of_birth = Column(Date())
    date_of_death = Column(Date())
    sex = Column(String(1))
    admissions = relationship("Admission", back_populates="patient",
                              cascade="all, delete, delete-orphan")
    active = Column(Boolean)


class Admission(Base):
    id = Column(Integer, primary_key=True)

    patient_id = Column(Integer, ForeignKey('patient.id'))
    patient = relationship("Patient", back_populates="admissions")

    bed_id = Column(Integer, ForeignKey('bed.id'))
    bed = relationship("Bed", foreign_keys=[bed_id], back_populates="admission")

    discharged_bed_id = Column(Integer, ForeignKey('bed.id'))
    discharged_bed = relationship("Bed", foreign_keys=[discharged_bed_id],
                                  back_populates="previous_admissions")

    admitted_date = Column(Date())
    discharged_date = Column(Date())

    admitting_doctor_id = Column(Integer, ForeignKey('doctor.id'))
    admitting_doctor = relationship("Doctor", back_populates="admissions")

    #diagnoses = relationship("Diagnosis")
    main_conditions = relationship("MainCondition")
    other_conditions = relationship("OtherCondition")

    admission_notes = Column(Text())
    progress_notes = Column(Text())
    discharge_advice = Column(Text())

    daily_rxs = relationship("DailyRx")

    discharge_rxs = relationship("DischargeRx")


class Bed(Base):
    id = Column(Integer, primary_key=True)

    number = Column(String(250))

    ward_id = Column(Integer, ForeignKey('ward.id'))
    ward = relationship("Ward", back_populates="beds")

    admission = relationship("Admission", uselist=False, back_populates="bed",
                             foreign_keys="Admission.bed_id")
    previous_admissions = relationship("Admission", back_populates="discharged_bed",
                                       foreign_keys="Admission.discharged_bed_id")


class Ward(Base):
    id = Column(Integer, primary_key=True)

    name = Column(String(250))
    bed_prefix = Column(String(250))

    beds = relationship("Bed", back_populates="ward")


class MainCondition(Base):
    id = Column(Integer, primary_key=True)

    admission_id = Column(Integer, ForeignKey('admission.id'))
    admission = relationship("Admission", back_populates="main_conditions")

    icd10class_code = Column(Integer, ForeignKey('icd10class.code'))
    icd10class = relationship("Icd10Class")

    icd10modifier_class_code = Column(Integer, ForeignKey('icd10modifierclass.code'))
    icd10modifier_class = relationship("Icd10ModifierClass",
                                       foreign_keys=[icd10modifier_class_code])

    icd10modifier_extra_class_code = Column(Integer, ForeignKey('icd10modifierclass.code'))
    icd10modifier_extra_class = relationship("Icd10ModifierClass",
                                             foreign_keys=[icd10modifier_extra_class_code])

    date = Column(Date())

    comment = Column(Text())


class OtherCondition(Base):
    id = Column(Integer, primary_key=True)

    admission_id = Column(Integer, ForeignKey('admission.id'))
    admission = relationship("Admission", back_populates="other_conditions")

    icd10class_code = Column(Integer, ForeignKey('icd10class.code'))
    icd10class = relationship("Icd10Class")

    icd10modifier_class_code = Column(Integer, ForeignKey('icd10modifierclass.code'))
    icd10modifier_class = relationship("Icd10ModifierClass",
                                       foreign_keys=[icd10modifier_class_code])

    icd10modifier_extra_class_code = Column(Integer, ForeignKey('icd10modifierclass.code'))
    icd10modifier_extra_class = relationship("Icd10ModifierClass",
                                             foreign_keys=[icd10modifier_extra_class_code])

    date = Column(Date())

    comment = Column(Text())


class DischargeRx(Base):
    id = Column(Integer, primary_key=True)

    admission_id = Column(Integer, ForeignKey('admission.id'))
    #admission = relationship("Admission", back_populates="discharge_rxs")
    drug_id = Column(Integer, ForeignKey('drug.id'))
    drug = relationship("Drug")
    drug_order = Column(String(250))
    active = Column(Boolean)


class DailyRx(Base):
    id = Column(Integer, primary_key=True)

    admission_id = Column(Integer, ForeignKey('admission.id'))
    #admission = relationship("Admission", back_populates="daily_rxs")
    drug_id = Column(Integer, ForeignKey('drug.id'))
    drug = relationship("Drug")
    drug_order = Column(String(250))
    active = Column(Boolean)


class Drug(Base):
    id = Column(Integer, primary_key=True)

    name = Column(String(250))


class Doctor(Base):
    id = Column(Integer, primary_key=True)

    name = Column(String(250))
    pmr_no = Column(String(250))
    admissions = relationship("Admission", back_populates="admitting_doctor")


class Preset(Base):
    id = Column(Integer, primary_key=True)

    name = Column(String(250))
    rxs = relationship("PresetRx", back_populates="preset", cascade="all, delete, delete-orphan")


class PresetRx(Base):
    id = Column(Integer, primary_key=True)

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
