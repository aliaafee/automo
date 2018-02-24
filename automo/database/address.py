"""Addresses of patients"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base

class Address(Base):
    """Patient addresses"""
    id = Column(Integer, primary_key=True)

    line_1 = Column(String(255))
    line_2 = Column(String(255))
    line_3 = Column(String(255))
    city = Column(String(255))
    region = Column(String(255))
    country = Column(String(255))

    permanent_residents = relationship("Patient", back_populates="permanent_address",
                                       foreign_keys="Patient.permanent_address_id")
    
    current_residents = relationship("Patient", back_populates="current_address",
                                       foreign_keys="Patient.current_address_id")

    def __repr__(self):
        return ", ".join(
            [ v for v in
                [
                    self.line_1,
                    self.line_2,
                    self.city,
                    self.region,
                    self.country
                ] 
            if v is not None]
        )
