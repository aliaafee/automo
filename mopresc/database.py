from sqlalchemy.dialects.sqlite.base import dialect
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Integer, String, ForeignKey, DateTime, Float, Text, Boolean
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref


Session = sessionmaker()


class Base(object):
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()

    id = Column(Integer, primary_key=True)


Base = declarative_base(cls=Base)


class Patient(Base):
    hospital_no = Column(String(10))
    national_id_no = Column(String(10))
    name = Column(String(250))
    age = Column(String(250))
    sex = Column(String(1))
    bed_no = Column(String(5))
    diagnosis = Column(String(250))
    rxs = relationship("Rx", back_populates="patient", cascade="all, delete, delete-orphan")


class Rx(Base):
    __tablename__ = 'rx'
    patient_id = Column(Integer, ForeignKey('patient.id'))
    patient = relationship("Patient", back_populates="rxs")
    drug_name = Column(String(250))
    drug_order = Column(String(250))
    active = Column(Boolean)


class Drug(Base):
    name = Column(String(250))


def StartEngine(uri):
    engine = create_engine(uri, echo=False)

    Base.metadata.create_all(engine)

    Session.configure(bind=engine)

    """
    session = Session()

    new_pt = Patient(
                  hospital_no = "10021",
                  national_id_no = "A046974",
                  name = "John Good Wind",
                  age = 29,
                  sex = "M",
                  bed_no = "SW45",
                  diagnosis = "Broken Bone" )
    
    new_pt.rxs = [
        Rx(drug_name = "T. Paracetamol 500mg", drug_order = "PO TDS x 7 days", active=True),
        Rx(drug_name = "T. Metronidazole 400mg", drug_order = "PO TDS x 7 days", active=True) ]
    
    
    session.add(new_pt)
    session.commit()
    """
