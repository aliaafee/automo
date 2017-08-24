"""Icd10 Classification"""

from sqlalchemy import Column, ForeignKey, String, Text, Enum
from sqlalchemy.orm import relationship, backref

from .base import Base


class Icd10Modifier(Base):
    """Icd10 Modifiers of classes"""
    code = Column(String(10), primary_key=True)

    name = Column(String(250))

    text = Column(Text())
    note = Column(Text())
    classes = relationship("Icd10ModifierClass")


class Icd10ModifierClass(Base):
    """Icd10 Individual Modifier Codes"""
    code = Column(String(20), primary_key=True)

    code_short = Column(String(10))

    preferred = Column(String(250))
    definition = Column(Text())
    inclusion = Column(Text())
    exclusion = Column(Text())

    modifier_code = Column(String(10), ForeignKey('icd10modifier.code'))
    modifier = relationship("Icd10Modifier", back_populates="classes")


class Icd10Class(Base):
    """Icd10 chapters, blocks and categories as a tree structure"""
    code = Column(String(10), primary_key=True)

    kind = Column(Enum("chapter", "block", "category"))

    preferred_plain = Column(String(250))

    preferred = Column(String(250))
    preferred_long = Column(Text())
    inclusion = Column(Text())
    exclusion = Column(Text())
    text = Column(Text())
    note = Column(Text())
    coding_hint = Column(Text())

    usage = Column(Enum("dagger", "aster"), name="usage")

    modifier_code = Column(String(10), ForeignKey('icd10modifier.code'))
    modifier = relationship("Icd10Modifier", foreign_keys=[modifier_code])

    modifier_extra_code = Column(String(10), ForeignKey('icd10modifier.code'))
    modifier_extra = relationship("Icd10Modifier", foreign_keys=[modifier_extra_code])

    parent_code = Column(String(10), ForeignKey("icd10class.code"))
    children = relationship('Icd10Class',
                            backref=backref("parent", remote_side='Icd10Class.code'))

    chapter_code = Column(String(10))
    parent_block_code = Column(String(10))

    problems = relationship("Problem", back_populates="icd10class")
