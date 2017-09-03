"""Admission Encounter"""
import datetime

from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from .encounter import Encounter

class Admission(Encounter):
    """Admission Encounter. Each hospital stay is associated with a bed, when the
      patient is discharged after the hospital stay, the bed attribute is cleared and the bed
      number is moved to the discharged_bed attribute."""
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'admission',
    }

    bed_id = Column(Integer, ForeignKey('bed.id'))
    bed = relationship("Bed", foreign_keys=[bed_id], back_populates="admission")

    discharged_bed_id = Column(Integer, ForeignKey('bed.id'))
    discharged_bed = relationship("Bed", foreign_keys=[discharged_bed_id],
                                  back_populates="previous_admissions")

    admission_note = Column(Text)
    progress_note = Column(Text)
    discharge_note = Column(Text)

    def end(self, end_time=datetime.datetime.now()):
        """Ends the admission"""
        super(Admission, self).end(end_time)

        self.discharged_bed = self.bed
        self.bed = None
