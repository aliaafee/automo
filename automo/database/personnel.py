"""Personnel"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .base import Base


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

    active = Column(Boolean)

    encounters = relationship("Encounter", back_populates="personnel")


class Doctor(Personnel):
    """Doctors, has list of encounters doctor had with patient."""
    id = Column(Integer, ForeignKey('personnel.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'doctor',
    }

    pmr_no = Column(String(250))

    #started_medications = relationship("Prescription", back_populates="started_by",
    #                                   foreign_keys="Prescription.started_by_id")
    #stopped_medications = relationship("Prescription", back_populates="stopped_by",
    #                                   foreign_keys="Prescription.stopped_by_id")

    def __repr__(self):
        if self.pmr_no is None:
            return "{0}".format(self.name)
        return "{0} ({1})".format(self.name, self.pmr_no)


class Nurse(Personnel):
    """Nurses."""
    id = Column(Integer, ForeignKey('personnel.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'nurse',
    }

    pnr_no = Column(String(250))

    def __repr__(self):
        
        return "{0} ({1})".format(self.name, self.pnr_no)
