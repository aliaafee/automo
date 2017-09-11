"""Prescription"""
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship

from .base import Base


class Prescription(Base):
    """Patient Prescription"""
    id = Column(Integer, primary_key=True)

    clinicalencounter_id = Column(Integer, ForeignKey('clinicalencounter.id'))
    clinicalencounter = relationship("Admission", back_populates="prescription")

    #date_from = Column(Date())
    #date_to = Column(Date())

    #started_by_id = Column(Integer, ForeignKey('doctor.id'))
    #started_by = relationship("Doctor", foreign_keys=[started_by_id],
    #                          back_populates="started_medications")

    #stopped_by_id = Column(Integer, ForeignKey('doctor.id'))
    #stopped_by = relationship("Doctor", foreign_keys=[stopped_by_id],
    #                          back_populates="stopped_medications")

    drug_id = Column(Integer, ForeignKey('drug.id'))
    drug = relationship("Drug")
    drug_order = Column(String(250))
    active = Column(Boolean)