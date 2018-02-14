"""Surgical Procedure"""
from sqlalchemy import Column, Integer, ForeignKey, Text, Boolean

from .encounter import Encounter


class SurgicalProcedure(Encounter):
    """Surgical Procedure.
      The post operative diagnosis will be the problems associated with this
      encounter. Preoperative diagnosis will written in uncoded text form. The encounter
      start time will be the time the patient is induced and the encounter time is the time
      patient is transferred to recovery room. The main operating surgeon will be the doctor
      for the encounter. """
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'surgicalprocedure'
    }

    assistant = Column(Text())
    anesthetist = Column(Text())
    nurse = Column(Text())

    emergency = Column(Boolean)

    preoperative_diagnosis = Column(Text())

    postoperative_diagnosis = Column(Text())

    procedure_name = Column(Text())

    findings = Column(Text())

    steps = Column(Text())
