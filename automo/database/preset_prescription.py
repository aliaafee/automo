"""Preset Prescription"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .base import Base


class PresetPrescription(Base):
    """Preset Drug Regimens"""
    id = Column(Integer, primary_key=True)

    name = Column(String(250))

    medications = relationship("PresetMedication", back_populates="preset", cascade="all, delete, delete-orphan")


class PresetMedication(Base):
    """Medication order in a drug regimen, duration is in days"""
    id = Column(Integer, primary_key=True)

    preset_id = Column(Integer, ForeignKey('presetprescription.id'))
    preset = relationship("PresetPrescription", back_populates="medications")

    drug_id = Column(Integer, ForeignKey('drug.id'))
    drug = relationship("Drug")
    drug_order = Column(String(250))
    active = Column(Boolean)
