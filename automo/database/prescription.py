"""Prescription"""
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship

from .base import Base


class Prescription(Base):
    """Patient Prescription"""
    id = Column(Integer, primary_key=True)

    clinicalencounter_id = Column(Integer, ForeignKey('clinicalencounter.id'))
    clinicalencounter = relationship("Admission", back_populates="prescription")

    drug_id = Column(Integer, ForeignKey('drug.id'))
    drug = relationship("Drug", back_populates="prescriptions")
    drug_order = Column(String(250))
    active = Column(Boolean)