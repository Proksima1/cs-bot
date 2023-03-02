from sqlalchemy import Column, Integer, Boolean, DATETIME, String, VARCHAR

from .database import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    nickname = Column(VARCHAR(100))
    is_admin = Column(Boolean)


class Log(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DATETIME)
    message = Column(VARCHAR(1000))