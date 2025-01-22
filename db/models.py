from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime


class Base(DeclarativeBase):
    pass


class TotalLines(Base):
    __tablename__ = "total_lines"

    id = Column(Integer, primary_key=True)
    total_lines = Column(Integer)
    date = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<TotalLines(total_lines={self.total_lines}, date={self.date})>"
