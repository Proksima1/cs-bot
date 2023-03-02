import sqlalchemy.exc
from sqlalchemy.exc import IntegrityError

from .database import session
from .schemas import User, Log
from datetime import datetime


def register_user(user_id: int, name, is_admin: bool):
    try:
        data = find_user(user_id)
    except sqlalchemy.exc.PendingRollbackError:
        session.rollback()
        return register_user(user_id, name, is_admin)
    if data:
        data.nickname = name
    else:
        user = User(
            user_id=user_id,
            is_admin=is_admin,
            nickname=name
        )
        session.add(user)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()


def find_user(id):
    user = session.query(User).filter_by(user_id=id).first()
    return user if user is not None else None


def select_users():
    users = session.query(User).all()
    return users


def add_log(message):
    log = Log(
        timestamp=datetime.now(),
        message=message
    )
    session.add(log)
    
    try:
        session.commit()
    except IntegrityError:
        session.rollback()


def select_admins():
    users = session.query(User).filter_by(is_admin=True)
    return [i.user_id for i in users]


def set_admin(id):
    try:
        user = session.query(User).filter_by(user_id=id).first()
    except sqlalchemy.exc.PendingRollbackError:
        session.rollback()
        return set_admin(id)
    if user is not None:
        user.is_admin = True
    else:
        register_user(id, '123', True)
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False


def delete_admin(id):
    try:
        user = session.query(User).filter_by(user_id=id).first()
    except sqlalchemy.exc.PendingRollbackError:
        session.rollback()
        return delete_admin(id)
    user.is_admin = False
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()
        return False
