"""User management"""
from sqlalchemy.orm.exc import NoResultFound

import exception
import database as db

CURRENT_USER = None


def get_current_user_id():
    """Return currently logged in user_id"""
    if CURRENT_USER is None:
        return None

    return CURRENT_USER.id 


def login_user(session, username, password):
    global CURRENT_USER

    try:
        user = session.query(db.User).filter(db.User.username == username).one()
    except NoResultFound:
        raise exception.AutoMOError("Login Error")

    result = user.verify_password(password)

    if result is False:
        raise exception.AutoMOError("Login Error")

    CURRENT_USER = user    
    return user


def logout_user(session):
    global CURRENT_USER
    CURRENT_USER = None
    return True
