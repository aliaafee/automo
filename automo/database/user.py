"""Users"""
from sqlalchemy import Column, Integer, String
from sqlalchemy_continuum import plugins

from .. import usermanager
from .base import Base

class User(Base):
    """Database Users"""
    id = Column(String(255), primary_key=True)

    name = Column(String(255))


class UserPlugin(plugins.base.Plugin):
    """Plugin for sqlalchemy continuum to record users for transactions"""
    def transaction_args(self, uow, session):
        return {
            'user_id': usermanager.get_current_user_id(),
        }
