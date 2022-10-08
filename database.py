import time

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from sqlalchemy import Column, Integer, String, ForeignKey

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Folder(Base):
    __tablename__ = "FOLDER_ID"

    id = Column(Integer, primary_key=True, index=True)
    folder_id = Column(String, unique=True)


class Token(Base):
    __tablename__ = "TOKEN"

    id = Column(Integer, primary_key=True, index=True)
    rclone_token = Column(String, unique=True)
    client_id = Column(String)
    client_secret = Column(String)


class Worker(Base):
    __tablename__ = "WORKER"

    id = Column(Integer, primary_key=True, index=True)
    folder_id = Column(String, ForeignKey("FOLDER_ID.id"), unique=True)
    token_id = Column(String, ForeignKey("TOKEN.id"), unique=True)
    worker_id = Column(String, nullable=False)
    last_activity = Column(Integer, default=int(time.time()))
