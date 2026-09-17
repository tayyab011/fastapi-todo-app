from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
SQLALCHEMY_DATABASE_URI = 'sqlite:///./todosapp.db'
#SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@localhost:3306/todoapplication'
engine = create_engine(SQLALCHEMY_DATABASE_URI , connect_args={"check_same_thread": False}) #needs for sqlite 3 
#engine = create_engine(SQLALCHEMY_DATABASE_URI ) eta postgresql er jonne lagbe
#engine = create_engine(SQLALCHEMY_DATABASE_URI) #eta mysql er jonne lagbe
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
""" pip install psycopg2-binary  for postgresql database"""
""" pip install pymysql  for mysql database"""