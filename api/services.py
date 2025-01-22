from db.models import (
    DBTotalContributions,
    DBLanguageUsage,
    DBTotalLines,
    DBLastYearContributions,
)
from sqlalchemy.orm import Session


def get_db_last_year_contributions(db: Session) -> DBLastYearContributions:
    contributions = db.query(DBLastYearContributions).all()
    return contributions


def get_db_total_contributions(db: Session) -> DBTotalContributions:
    contributions = db.query(DBTotalContributions).all()
    return contributions


def get_db_language_usage(db: Session) -> list[DBLanguageUsage]:
    language_usage = db.query(DBLanguageUsage).all()
    return language_usage


def get_db_total_lines(db: Session) -> DBTotalLines:
    total_lines = db.query(DBTotalLines).first()
    return total_lines
