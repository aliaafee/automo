"""Notes"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from .base import Base


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

    clinicalencounter_id = Column(Integer, ForeignKey('clinicalencounter.id'))
    clinicalencounter = relationship("ClinicalEncounter", back_populates="notes")


class History(Note):
    """Patient History Note"""
    id = Column(Integer, ForeignKey('note.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'history',
    }

    chief_complaints = Column(Text())
    presenting_illness = Column(Text())
    past = Column(Text())
