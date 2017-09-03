"""Measurements"""
from sqlalchemy import Column, Integer, ForeignKey, Float

from .encounter import Encounter


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
