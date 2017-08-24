"Drug"
from sqlalchemy import Column, Integer, String

from .base import Base

class Drug(Base):
    """Drugs"""
    id = Column(Integer, primary_key=True)

    name = Column(String(250))

    def __repr__(self):
        return self.name