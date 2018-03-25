"""Users"""
from passlib.hash import pbkdf2_sha256
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy_continuum import plugins

from .. import loginmanager
from .base import Base

class User(Base):
    """Database Users"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    username = Column(String(60))
    fullname = Column(String(255))
    password_hash = Column(String(128))

    active = Column(Boolean, default=True)

    personnel_id = Column(Integer, ForeignKey('personnel.id'))
    personnel = relationship("Personnel", back_populates="user")

    @property
    def password(self):
        """Prevent Password from being accessed"""
        raise AttributeError("Password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    def verify_password(self, password):
        """Verify password"""
        if self.password_hash is None:
            return False
        return pbkdf2_sha256.verify(password, self.password_hash)


class UserPlugin(plugins.base.Plugin):
    """Plugin for sqlalchemy continuum to record users for transactions"""
    def transaction_args(self, uow, session):
        return {
            'user_id': loginmanager.get_current_user_id(),
        }
