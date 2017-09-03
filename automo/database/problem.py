"""Problem"""

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text, String
from sqlalchemy.orm import relationship

from . import dbexception
from .base import Base
from .problem_encounter import problem_encounter_association_table


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

    start_time = Column(DateTime())
    end_time = Column(DateTime())

    encounters = relationship("Encounter",
                              secondary=problem_encounter_association_table,
                              back_populates="problems")

    comment = Column(Text)

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
        if self.patient != encounter.patient:
            raise dbexception.AutoMODatabaseError("The Problem and Encounter should be from the same patient")

        if encounter in self.encounters:
            raise dbexception.AutoMODatabaseError("This encounter already exists in this problem")

        self.encounters.append(encounter)


    def __repr__(self):
        if self.icd10class is not None:
            return '<Problem "{0}">'.format(self.icd10class.preferred_plain)
        return '<Problem>'
