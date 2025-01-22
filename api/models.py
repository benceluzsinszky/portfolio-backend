from pydantic import BaseModel
from datetime import datetime


class LastYearContributions(BaseModel):
    id: int
    date: datetime
    count: int
    level: int
    date_created: datetime


class TotalContributions(BaseModel):
    id: int
    total_contributions: int
    date_created: datetime


class LanguageUsage(BaseModel):
    id: int
    language: str
    count: int
    date_created: datetime


class TotalLines(BaseModel):
    id: int
    total_lines: int
    date_created: datetime
