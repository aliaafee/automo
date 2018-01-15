"""Complication Grades"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy import event

from .base import Base

class ComplicationGrade(Base):
    """Complication Grades, graded by clavian-dindo."""
    id = Column(String(5), primary_key=True)

    description = Column(Text)

    admissions = relationship("Admission", back_populates="complication_grade",
                              foreign_keys="Admission.complication_grade_id")

    def __repr__(self):
        return "Grade {0}".format(self.id, self.description)
