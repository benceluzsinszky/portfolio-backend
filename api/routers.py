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


@router.get("/contributions")
@limiter.limit("10/minute")
async def get_contributions(
    request: Request, last: bool | None = None, db: Session = Depends(get_db)
) -> list[LastYearContributions] | list[TotalContributions]:
    print(last)
    try:
        if last:
            contributions = get_db_last_year_contributions(db)
            return contributions
        else:
            contributions = get_db_total_contributions(db)
            return contributions

    except NoResultFound:
        raise HTTPException(status_code=204, detail="No contributions in DB")


@router.get("/language_usage")
@limiter.limit("10/minute")
async def get_language_usage(
    request: Request, db: Session = Depends(get_db)
) -> list[LanguageUsage]:
    language_usage = get_db_language_usage(db)
    print(language_usage)
    if not language_usage:
        raise HTTPException(status_code=204, detail="No language usage in DB")

    return language_usage


@router.get("/total_lines")
@limiter.limit("10/minute")
async def get_total_lines(
    request: Request, db: Session = Depends(get_db)
) -> TotalLines:
    total_lines = get_db_total_lines(db)
    if not total_lines:
        raise HTTPException(status_code=204, detail="No total lines in DB")

    return total_lines
