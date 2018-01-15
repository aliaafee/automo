"""Clinical Encounter"""
from sqlalchemy import Column, Integer, ForeignKey, Text, String, Boolean
from sqlalchemy.orm import relationship

from .encounter import Encounter
from .. import dbexception
from ..drug import Drug
from ..prescription import Prescription
from ..complicationgrade import ComplicationGrade
from .surgicalprocedure import SurgicalProcedure


class ClinicalEncounter(Encounter):
    """Base class of all clinical encounters, which are admissions and outpatient
      enconters. Each clinicalencounter is associated with a prescription"""
    id = Column(Integer, ForeignKey('encounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'clinicalencounter',
    }

    label = "Clinical Encounter"

    chief_complaints = Column(Text)
    history = Column(Text)
    past_history = Column(Text)

    general_inspection = Column(Text)
    exam_head = Column(Text)
    exam_neck = Column(Text)
    exam_chest = Column(Text)
    exam_abdomen = Column(Text)
    exam_genitalia = Column(Text)
    exam_pelvic_rectal = Column(Text)
    exam_extremities = Column(Text)
    exam_other = Column(Text)

    notes = relationship("Note", back_populates="clinicalencounter",
                         cascade="all, delete, delete-orphan")

    prescription = relationship("Prescription", back_populates="clinicalencounter",
                                cascade="all, delete, delete-orphan")

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




class Admission(ClinicalEncounter):
    """Admission Encounter. Each hospital stay is associated with a bed, when the
      patient is discharged after the hospital stay, the bed attribute is cleared and the bed
      number is moved to the discharged_bed attribute."""
    id = Column(Integer, ForeignKey('clinicalencounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'admission',
    }

    label = "Admission"

    bed_id = Column(Integer, ForeignKey('bed.id'))
    bed = relationship("Bed", foreign_keys=[bed_id], back_populates="admission")

    discharged_bed_id = Column(Integer, ForeignKey('bed.id'))
    discharged_bed = relationship("Bed", foreign_keys=[discharged_bed_id],
                                  back_populates="previous_admissions")

    #admission_note = Column(Text)
    #progress_note = Column(Text)
    #discharge_note = Column(Text)
    hospital_course = Column(Text)
    discharge_advice = Column(Text)
    follow_up = Column(Text)

    complication_grade_id = Column(String(5), ForeignKey('complicationgrade.id'))
    complication_grade = relationship("ComplicationGrade", foreign_keys=[complication_grade_id],
                                      back_populates="admissions")
    complication_summary = Column(Text)
    complication_disability = Column(Boolean)


    def end(self, session, end_time=None):
        """Ends the admission"""

        if self.complication_grade_id is None:
            surgical_enounters = session.query(SurgicalProcedure)\
                                    .filter(SurgicalProcedure.parent == self)
            if surgical_enounters.count() == 0:
                print "No surgical procedures so None complication grade allowed"
            else:
                raise dbexception.AutoMODatabaseError("Surgical Complication Grade should be assigned before discharge.")
                return

        super(Admission, self).end(session, end_time)

        self.discharged_bed = self.bed
        self.bed = None



class CircumcisionAdmission(Admission):
    """Admission Encounter. Each hospital stay is associated with a bed, when the
      patient is discharged after the hospital stay, the bed attribute is cleared and the bed
      number is moved to the discharged_bed attribute."""
    id = Column(Integer, ForeignKey('admission.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'circumcisionadmission',
    }

    label = "Circumcision"

    preoperative_orders = Column(Text)



class OutpatientEncounter(ClinicalEncounter):
    """Visit to outpatient clinic"""
    id = Column(Integer, ForeignKey('clinicalencounter.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity':'outpatientencounter',
    }

    label = "Outpatient"

    room = Column(String(50))
