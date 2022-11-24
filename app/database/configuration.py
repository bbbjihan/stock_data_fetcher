from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
import pymysql
from itertools import chain


engine = create_engine(settings.MYSQL_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=engine)

def get_db():
    """
    Get the database session
    Yields:
        Session: The database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()