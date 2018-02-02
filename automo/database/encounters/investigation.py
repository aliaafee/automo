"""Investigation"""
from sqlalchemy import Column, Integer, ForeignKey, Float, Text, String

from .encounter import Encounter


class Investigation(Encounter):
    """Investigation"""
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'investigation',
    }

    def set_record_time(self, record_time):
        """In this encounter start-time and end-time are same, use this attr
          to change both at the same time"""
        self.start_time = record_time
        self.end_time = record_time

    def get_record_time(self):
        """In this encounter start-time and end-time are same, use this attr
          to change both at the same time"""
        return self.start_time

    record_time = property(get_record_time, set_record_time, None,
                           "Time this parameter was recorded.")


class Imaging(Investigation):
    """Imaging."""
    id = Column(Integer, ForeignKey('investigation.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity':'imaging'
    }

    site = Column(String(255))
    imaging_type = Column(String(255))
    report = Column(Text)
    impression = Column(Text)
    radiologist = Column(String(255))


class Endoscopy(Investigation):
    """Endoscopy."""
    id = Column(Integer, ForeignKey('investigation.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity':'endoscopy'
    }

    site = Column(String(255))
    report = Column(Text)
    impression = Column(Text)
    endoscopist = Column(String(255))


class Histopathology(Investigation):
    """Histopathology."""
    id = Column(Integer, ForeignKey('investigation.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity':'histopathology'
    }

    site = Column(String(255))
    report = Column(Text)
    impression = Column(Text)
    pathologist = Column(String(255))


class CompleteBloodCount(Investigation):
    """CompleteBloodCount.
      hemoglobin (Hemoglobin) in g% 
      tlc (Total Leucocyte Count) 10^9/L
      plt (Platelate Count) 10^9/L
      dlc_n (DLC Nutrophils) %
      dlc_l (DLC Lymphocytes) %
      dlc_m (DLC Monocytes) %
      dlc_e (DLC Monocytes) %"""
    id = Column(Integer, ForeignKey('investigation.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity':'completebloodcount'
    }

    hemoglobin = Column(Float)
    tlc = Column(Float)
    plt = Column(Float)
    dlc_n = Column(Float)
    dlc_l = Column(Float)
    dlc_m = Column(Float)
    dlc_e = Column(Float)


class RenalFunctionTest(Investigation):
    """RenalFunctionTest.
      urea (Serum Urea) mmol/L
      creatinine (Serum Creatinine) mmol/L"""
    id = Column(Integer, ForeignKey('investigation.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity':'renalfunctiontest'
    }

    urea = Column(Float)
    creatinine = Column(Float)


class LiverFunctionTest(Investigation):
    """LiverFunctionTest.
      t_bil (Total Billirubin) mmol/L
      d_bil (Direct Billirubin) mmol/L
      alt (Alanine Amino Transferase) U/L
      ast (Aspartate Amino Transferase) U/L
      alp (Alkaline Phosphatase) U/L"""
    id = Column(Integer, ForeignKey('investigation.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity':'liverfunctiontest'
    }

    t_bil = Column(Float)
    d_bil = Column(Float)
    alt = Column(Float)
    ast = Column(Float)
    alp = Column(Float)


class OtherTest(Investigation):
    """Other Test.
      name Name of the test
      value Result of the test, can be numerical or text
      unit Unit of the result, if applicable"""

    id = Column(Integer, ForeignKey('investigation.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity':'othertest'
    }

    name = Column(String(255))
    value = Column(String(255))
    unit = Column(String(255))
