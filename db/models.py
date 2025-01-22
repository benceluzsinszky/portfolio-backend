from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime


class Base(DeclarativeBase):
    pass


class DBLastYearContributions(Base):
    __tablename__ = "last_year_contributions"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    count = Column(Integer)
    level = Column(Integer)
    date_created = Column(DateTime, default=datetime.now)


class DBTotalContributions(Base):
    __tablename__ = "total_contributions"

    id = Column(Integer, primary_key=True)
    total_contributions = Column(Integer)
    date_created = Column(DateTime, default=datetime.now)


class DBLanguageUsage(Base):
    __tablename__ = "language_usage"

    id = Column(Integer, primary_key=True)
    language = Column(String)
    count = Column(Integer)
    date_created = Column(DateTime, default=datetime.now)


class DBTotalLines(Base):
    __tablename__ = "total_lines"

    id = Column(Integer, primary_key=True)
    total_lines = Column(Integer)
    date_created = Column(DateTime, default=datetime.now)
