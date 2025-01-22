from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, DateTime, String
from datetime import datetime


class Base(DeclarativeBase):
    pass


class LastYearContributions(Base):
    __tablename__ = "last_year_contributions"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime)
    count = Column(Integer)
    level = Column(Integer)
    date_created = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<LastYearContributions(last_year_contributions={self.last_year_contributions}, date={self.date})>"


class TotalContributions(Base):
    __tablename__ = "total_contributions"

    id = Column(Integer, primary_key=True)
    total_contributions = Column(Integer)
    date_created = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<TotalContributions(total_contributions={self.total_contributions}, date={self.date})>"


class LanguageUsage(Base):
    __tablename__ = "language_usage"

    id = Column(Integer, primary_key=True)
    language = Column(String)
    count = Column(Integer)
    date_created = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<LanguageUsage(language={self.language}, count={self.count}, date={self.date})>"


class TotalLines(Base):
    __tablename__ = "total_lines"

    id = Column(Integer, primary_key=True)
    total_lines = Column(Integer)
    date_created = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<TotalLines(total_lines={self.total_lines}, date={self.date})>"
