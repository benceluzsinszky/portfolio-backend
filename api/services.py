from db.models import (
    DBTotalContributions,
    DBLanguageUsage,
    DBTotalLines,
    DBLastYearContributions,
)
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound


def get_db_last_year_contributions(db: Session) -> DBLastYearContributions:
    contributions = db.query(DBLastYearContributions).all()
    if not contributions:
        raise NoResultFound
    return contributions


def get_db_total_contributions(db: Session) -> DBTotalContributions:
    contributions = db.query(DBTotalContributions).one()
    return contributions


def get_db_language_usage(db: Session) -> list[DBLanguageUsage]:
    language_usage = db.query(DBLanguageUsage).all()
    if not language_usage:
        raise NoResultFound
    return language_usage


def get_db_total_lines(db: Session) -> DBTotalLines:
    total_lines = db.query(DBTotalLines).one()

    return total_lines
