from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from config import settings

# reminder: establish a connection to to postgresql
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

# reminder: create a session factory for interacting with the database
SessionLocal: sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

db: Session = SessionLocal()
