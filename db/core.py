from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
import dotenv
import os

dotenv.load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))
session_local = sessionmaker(
    class_=Session, autocommit=False, autoflush=False, bind=engine
)
MetaData().create_all(bind=engine)


# Dependency to get the database session
def get_db():
    database = session_local()
    try:
        yield database
    finally:
        database.close()
