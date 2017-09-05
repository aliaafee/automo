"""Vital Signs"""
from sqlalchemy import Column, Integer, ForeignKey, Float

from .encounter import Encounter


class VitalSigns(Encounter):
    """Record Vital Signs.
      pulse_rate in beats per minute,
      respiratory_rate in breaths per minute,
      diastolic_bp and systolic_bp in mmHg, this is NIBP,
      temperature in degrees Celcius"""
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'vitalsigns',
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

    pulse_rate = Column(Float)
    respiratory_rate = Column(Float)
    diastolic_bp = Column(Float)
    systolic_bp = Column(Float)
    temperature = Column(Float)


class VitalSignsExtended(VitalSigns):
    """Record extended vital signs. extended VitalSigns with more variables
      in addition to signs in VitalSigns.
      cvp (central venous pressure) in mmHg 
      systolic_ibp and diastolic_ibp in mmHg
      cap_spo2 in % (capillary spo2)"""
    id = Column(Integer, ForeignKey('vitalsigns.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity':'vitalsignsextended'
    }

    cvp = Column(Float)
    systolic_ibp = Column(Float)
    diastolic_ibp = Column(Float)
    cap_spo2 = Column(Float)
