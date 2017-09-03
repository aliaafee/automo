"""Clinic Visit"""
from sqlalchemy import Column, Integer, ForeignKey, String

from .encounter import Encounter


class ClinicVisit(Encounter):
    """Clinic Visit Encounter"""
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'clinicvisit',
    }

    room = Column(String(50))