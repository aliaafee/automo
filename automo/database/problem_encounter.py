"""Problem Encounter Association Table"""
from sqlalchemy import Table, Column, Integer, ForeignKey

from .base import Base


problem_encounter_association_table = Table(
    'problem_encounter_association', Base.metadata,
    Column('problem_id', Integer, ForeignKey('problem.id')),
    Column('encounter_id', Integer, ForeignKey('encounter.id'))
)