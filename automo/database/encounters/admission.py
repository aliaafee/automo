"""Admission Encounter"""
import datetime

from sqlalchemy import Column, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from .encounter import Encounter
from .. import dbexception
from ..drug import Drug
from ..prescription import Prescription

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

    prescription = relationship("Prescription", back_populates="admission",
                                cascade="all, delete, delete-orphan")

    def end(self, end_time=None):
        """Ends the admission"""
        super(Admission, self).end(end_time)

        self.discharged_bed = self.bed
        self.bed = None


    def prescribe_drug(self, session, drug, drug_str, drug_order, active=True):
        """Precribe medication. Drug can be passed as an object, or object can be None
          and a string name of Drug can be passed. If this string name not found in drug list
          it will be added."""
        if drug is None:
            if drug_str == "":
                raise dbexception.AutoMODatabaseError("New drug name cannot be empty")
            query = session.query(Drug)\
                        .filter(Drug.name == drug_str)
            if query.count() == 0:
                new_drug = Drug(
                    name = drug_str
                )
                session.add(new_drug)
                drug = new_drug
            else:
                drug = query.first()
        new_presc = Prescription(
            drug = drug,
            drug_order = drug_order,
            active = active
        )
        self.prescription.append(new_presc)
