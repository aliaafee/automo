"""Bed"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base

class Bed(Base):
    """Bed in the clinic/hospital, each bed is associated with a HospitalStay,
      and a list of previous admissions in the bed."""
    id = Column(Integer, primary_key=True)

    number = Column(String(250))

    ward_id = Column(Integer, ForeignKey('ward.id'))
    ward = relationship("Ward", back_populates="beds")

    admission = relationship("Admission", uselist=False, back_populates="bed",
                             foreign_keys="Admission.bed_id")
    previous_admissions = relationship("Admission", back_populates="discharged_bed",
                                       foreign_keys="Admission.discharged_bed_id")

    def __repr__(self):
        if self.ward is None:
            return self.number
        return "{0} {1}".format(self.ward.bed_prefix, self.number)
