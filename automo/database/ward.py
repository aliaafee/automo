"Ward"
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from .base import Base


class Ward(Base):
    """Ward in the clinic/hospital, each ward has multiple beds"""
    id = Column(Integer, primary_key=True)

    name = Column(String(250))
    bed_prefix = Column(String(250))

    active = Column(Boolean, default=True)

    beds = relationship("Bed", back_populates="ward")

    def __repr__(self):
        return "{}".format(self.name)
