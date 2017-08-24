"""Encounters"""
import datetime

from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref

from . import dbexception
from .base import Base
from .problem_encounter import problem_encounter_association_table


class Encounter(Base):
    """The encounter that the patient had with health facility, each encounter
      can be for single or multiple problems. the encounter object can be polymorphic,
      eg: HospitalStay and ClinicVisit are child classes. Possiblity of expanding
      to include other kinds of encounters, and these child encounters can be extended
      furture with more child classes.
      Each encounter instance can have multiple child encounter instances, for example
      a HospitalStay encounter instance can have a SurgicalProcedure as a child encounter
      instance.
      Each encounter has a start time and end time, and is associated with a personnel, and 
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

    personnel_id = Column(Integer, ForeignKey('personnel.id'))
    personnel = relationship("Personnel", back_populates="encounters")

    problems = relationship("Problem",
                            secondary=problem_encounter_association_table,
                            back_populates="encounters")

    notes = relationship("Note", back_populates="encounter",
                         cascade="all, delete, delete-orphan")

    def add_problem(self, problem):
        """Add a problem to the encounter"""
        if self.patient != problem.patient:
            raise dbexception.AutoMODatabaseError("The Problem and Encounter should be from the same patient")
            return
        if problem in self.problems:
            raise dbexception.AutoMODatabaseError("This problem already exists in this encounter")
            return
        self.problems.append(problem)

    def add_child_encounter(self, encounter):
        """Add a child encounter"""
        self.children.append(encounter)

    def end(self, end_time=datetime.datetime.now()):
        if self.end_time is not None:
            raise dbexception.AutoMODatabaseError("This encounter has already ended")
        self.end_time = end_time


class Admission(Encounter):
    """Admission Encounter. Each hospital stay is associated with a bed, when the
      patient is discharged after the hospital stay, the bed attribute is cleared and the bed
      number is moved to the discharged_bed attribute."""
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'admission',
    }

    bed_id = Column(Integer, ForeignKey('bed.id'))
    bed = relationship("Bed", foreign_keys=[bed_id], back_populates="admission")

    discharged_bed_id = Column(Integer, ForeignKey('bed.id'))
    discharged_bed = relationship("Bed", foreign_keys=[discharged_bed_id],
                                  back_populates="previous_admissions")

    def end(self, end_time=datetime.datetime.now()):
        """Ends the admission"""
        super(Admission, self).end(end_time)

        self.discharged_bed = self.bed
        self.bed = None



class ClinicVisit(Encounter):
    """Clinic Visit Encounter"""
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'clinicvisit',
    }

    room = Column(String(50))


class Measurements(Encounter):
    """Record Anthropometric Measurements
      weight in kg, height in m"""
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'measurements'
    }

    weight = Column(Float)
    height = Column(Float)

    @property
    def bmi(self):
        if self.height == 0:
            return None
        return self.weight / (self.height ** 2)


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
