from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import Session
from db.core import get_db
from api.services import (
    get_db_last_year_contributions,
    get_db_total_contributions,
    get_db_language_usage,
    get_db_total_lines,
)
from api.models import (
    LastYearContributions,
    TotalContributions,
    LanguageUsage,
    TotalLines,
)
from api.limiter import limiter


router = APIRouter()


@router.get("/last_year_contributions")
@limiter.limit("10/minute")
async def get_last_year_contributions(
    request: Request, last: bool | None = None, db: Session = Depends(get_db)
) -> list[LastYearContributions]:
    try:
        contributions = get_db_last_year_contributions(db)
        return contributions

    except NoResultFound:
        raise HTTPException(status_code=204, detail="No contributions in DB")


@router.get("/total_contributions")
@limiter.limit("10/minute")
async def get_total_contributions(
    request: Request, last: bool | None = None, db: Session = Depends(get_db)
) -> TotalContributions:
    try:
        contributions = get_db_total_contributions(db)
        return contributions

    except NoResultFound:
        raise HTTPException(status_code=204, detail="No contributions in DB")


@router.get("/language_usage")
@limiter.limit("10/minute")
async def get_language_usage(
    request: Request, db: Session = Depends(get_db)
) -> list[LanguageUsage]:
    try:
        language_usage = get_db_language_usage(db)
        return language_usage

    except NoResultFound:
        raise HTTPException(status_code=204, detail="No contributions in DB")


@router.get("/total_lines")
@limiter.limit("10/minute")
async def get_total_lines(
    request: Request, db: Session = Depends(get_db)
) -> TotalLines:
    try:
        total_lines = get_db_total_lines(db)
        return total_lines

    except NoResultFound:
        raise HTTPException(status_code=204, detail="No contributions in DB")
