"""Other Encounter"""
from sqlalchemy import Column, Integer, ForeignKey, Text, String

from .encounter import Encounter


class OtherEncounter(Encounter):
    """Other Encounter
      To Record encounters that have not been specified elsewhere"""
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'otherencounter'
    }

    title = Column(String(255))
    note = Column(Text())