from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import warnings
from sqlalchemy.exc import ProgrammingError


USER = "k2u1yqycv3bodj4z"
PASSWORD = "l2gzxi58ynrq4pbd"
HOST = "tyduzbv3ggpf15sx.cbetxkdyhwsb.us-east-1.rds.amazonaws.com"
PORT = "3306"
DATABASE = "pmfkjy5n1gcwlin1"
engine = create_engine(
    f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}", pool_size=2
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
try:
    engine.execute(f"CREATE DATABASE {DATABASE}")
except ProgrammingError:
    warnings.warn(
        f"Could not create database {DATABASE}. Database {DATABASE} may already exist."
    )
    pass


engine.execute(f"USE {DATABASE}")
