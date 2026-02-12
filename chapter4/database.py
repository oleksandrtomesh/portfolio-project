from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

#SQLlite string
SQLALCHEMY_DATABASE_URL = 'sqlite:///./fantasy_data.db'

#Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={"check_same_thread": False})

#Set up session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False,
                            bind=engine)

Base = declarative_base()