"""Patient"""
import datetime
import dateutil.relativedelta

from sqlalchemy import Column, Integer, String, Date, Boolean, not_
from sqlalchemy.orm import relationship

from . import dbexception
from .base import Base
from .encounters import Encounter, Admission


class Patient(Base):
    """Patient demographic data and list of problems and encounters of the patient.
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

    def set_age(self, age, today=datetime.date.today()):
        """Set age of patient as relativedelta, age is not acctually stored,
          date of birth is calculated and stored"""
        self.date_of_birth = today - age

    def get_age(self):
        """Calculate and return age of patient as a relativedelta object"""
        if self.date_of_birth is None:
            return None
        return dateutil.relativedelta.relativedelta(datetime.date.today(), self.date_of_birth)

    age = property(get_age, set_age, None, "Age of the patient as relativedelta.")


    def get_current_encounter(self, session):
        """Get currently active encounter, an encounter is active when the end_time is None,
          Only one encounter should be active at a time. If a singe active enounter is not
          found raises AutoMODatabaseError"""
        active_encounters = session.query(Encounter)\
                                .filter(Encounter.patient == self)\
                                .filter(Encounter.end_time == None)

        if active_encounters.count() == 1:
            return active_encounters.one()
        elif active_encounters.count() > 1:
            raise dbexception.AutoMODatabaseError("Multiple active Encounters for patient found. This should not happen.")
        else:
            return None


    def discharge(self, session, discharge_time=datetime.datetime.now(), admission=None):
        """End the currently active admission, raises AutoMODatabase Error if their is no
          active admission"""
        if admission is None:
            current_encounter = self.get_current_encounter(session)
            if current_encounter is None:
                raise dbexception.AutoMODatabaseError("Patient has no active admissions.")
            if current_encounter.type != "admission":
                raise dbexception.AutoMODatabaseError("Current encounter is not an admission")
            admission = current_encounter

        admission.end(discharge_time)


    def admit(self, session, bed, admission_time=datetime.datetime.now()):
        """Admit the patient to the provided bed. If patient is already admitted or the bed
          is occupied, raises AutoMODatabaseError. Returns the created encounter object."""
        current_encounter = self.get_current_encounter(session)
        if current_encounter is not None:
            raise dbexception.AutoMODatabaseError("There is an active encounter, end it before admitting.")

        if bed.admission is not None:
            raise dbexception.AutoMODatabaseError("Bed {0} is already occupied.".format(bed))

        new_admission = Admission(
            patient = self,
            start_time = admission_time,
            bed = bed
        )

        session.add(new_admission)

        return new_admission
