"""Progress Note"""
from sqlalchemy import Column, Integer, ForeignKey, Text

from .encounter import Encounter


class Progress(Encounter):
    """Progress Note."""
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'progress'
    }

    def set_examination_time(self, examination_time):
        """In this encounter start-time and end-time are same, use this attr
          to change both at the same time"""
        self.start_time = examination_time
        self.end_time = examination_time

    def get_examination_time(self):
        """In this encounter start-time and end-time are same, use this attr
          to change both at the same time"""
        return self.start_time

    examination_time = property(get_examination_time, set_examination_time, None,
                           "Time patient was examined.")

    subjective = Column(Text())

    objective = Column(Text())

    assessment = Column(Text())

    plan = Column(Text())
