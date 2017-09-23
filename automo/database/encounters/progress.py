"""Progress Note"""
from sqlalchemy import Column, Integer, ForeignKey, Text

from .encounter import Encounter


class Progress(Encounter):
    """Progress Note."""
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'progress'
    }

    subjective = Column(Text())

    objective = Column(Text())

    assessment = Column(Text())

    plan = Column(Text())
