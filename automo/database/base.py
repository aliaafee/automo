"""Base db object"""
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base


class Base(object):
    """Base class for all tables"""
    @declared_attr
    def __tablename__(self):
        return self.__name__.lower()


Base = declarative_base(cls=Base)
