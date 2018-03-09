"Drug"
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base

class Drug(Base):
    """Drugs"""
    id = Column(Integer, primary_key=True)

    name = Column(String(250))

    prescriptions = relationship("Prescription", back_populates="drug")

    def merge_with(self, session, drugs):
        """Merges duplicate drug entries into one"""
        prescriptions = []
        for drug in drugs:
            if drug.prescriptions:
                prescriptions.extend(drug.prescriptions)
        for prescription in prescriptions:
            prescription.drug = self
        for drug in drugs:
            session.delete(drug)

    def __repr__(self):
        return self.name