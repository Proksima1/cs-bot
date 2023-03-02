from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from data.config import DATABASE_USERNAME,DATABASE_PASSWORD,DATABASE_IP,DATABASE_DB
# engine = create_engine('sqlite:///db.db')
# session = scoped_session(sessionmaker(bind=engine))
# Base = declarative_base()

engine = create_engine(f'mysql+mysqlconnector://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_IP}/{DATABASE_DB}?charset=utf8mb4',
                       pool_recycle=3600)
session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


def create_base():
    Base.metadata.create_all(engine)
