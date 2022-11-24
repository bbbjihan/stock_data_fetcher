from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
import pymysql
from itertools import chain

# from app.database.session import SessionLocal


engine = create_engine(settings.MYSQL_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# def check_requirement():
#     pymysql.connect(settings.MYSQL_DATABASE_URI)


# check_requirement()
