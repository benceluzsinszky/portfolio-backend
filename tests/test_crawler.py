import pytest
from unittest.mock import patch, mock_open
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from db.core import Base
from datetime import datetime
from crawler.crawler import Crawler
import requests

from db.models import (
    DBLastYearContributions,
    DBTotalContributions,
    DBLanguageUsage,
    DBTotalLines,
)

DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    class_=Session, autocommit=False, autoflush=False, bind=engine
)


@pytest.fixture(scope="session", autouse=True)
def run_before_and_after_tests():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture()
def crawler(db_session):
    return Crawler(username="test_user", token="test_token", db=db_session)


def test__fetch_repos_shouldberepos_when_responseok(crawler):
    with patch("requests.get") as mock_get:
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = [{"name": "repo1"}, {"name": "repo2"}]

        repos = crawler._fetch_repos()

        assert len(repos) == 2
        assert repos[0]["name"] == "repo1"
        assert repos[1]["name"] == "repo2"


def test__fetch_repos_shouldthrowexception_whenresponseisnotok(crawler):
    with patch("requests.get") as mock_get:
        mock_get.return_value.ok = False

        with pytest.raises(requests.exceptions.RequestException):
            crawler._fetch_repos()


def test_get_repos_shouldbeok_when_fetch_reposreturnrepos(crawler):
    with patch.object(
        crawler, "_fetch_repos", return_value=[{"name": "repo1"}, {"name": "repo2"}]
    ):
        crawler.get_repos()
        assert len(crawler.repos) == 2
        assert "repo1" in crawler.repos
        assert "repo2" in crawler.repos


def test_get_repos_shouldtnotupdaterepos_when_fetch_reposthrowsexception(crawler):
    with patch.object(
        crawler, "_fetch_repos", side_effect=requests.exceptions.RequestException
    ):
        crawler.get_repos()

        assert len(crawler.repos) == 0


def test__fetch_last_year_contributions_shouldreturncalendar_whenresponseok(crawler):
    with patch("requests.post") as mock_post:
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {
            "data": {
                "user": {
                    "contributionsCollection": {
                        "contributionCalendar": {
                            "weeks": [
                                {
                                    "contributionDays": [
                                        {
                                            "date": "2024-01-01",
                                            "contributionLevel": "FIRST_QUARTILE",
                                            "contributionCount": 1,
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        }

        calendar = crawler._fetch_last_year_contributions()

        assert len(calendar["weeks"]) == 1
        assert len(calendar["weeks"][0]["contributionDays"]) == 1
        assert calendar["weeks"][0]["contributionDays"][0]["date"] == "2024-01-01"
        assert (
            calendar["weeks"][0]["contributionDays"][0]["contributionLevel"]
            == "FIRST_QUARTILE"
        )
        assert calendar["weeks"][0]["contributionDays"][0]["contributionCount"] == 1


def test__parse_level_shouldreturnlevel_whenlevelisvalid(crawler):
    assert crawler._parse_level("FIRST_QUARTILE") == 1
    assert crawler._parse_level("SECOND_QUARTILE") == 2
    assert crawler._parse_level("THIRD_QUARTILE") == 3
    assert crawler._parse_level("FOURTH_QUARTILE") == 4
    assert crawler._parse_level("NONE") == 0
    assert crawler._parse_level("INVALID") == 0


def test__parse_calendar_shouldreturncalendar_whenresponse_calendarisvalid(crawler):
    calendar = {
        "weeks": [
            {
                "contributionDays": [
                    {
                        "date": "2024-01-01",
                        "contributionLevel": "FIRST_QUARTILE",
                        "contributionCount": 1,
                    }
                ]
            }
        ]
    }

    parsed_calendar = crawler._parse_calendar(calendar)

    assert len(parsed_calendar) == 1
    assert parsed_calendar[0]["date"] == datetime(2024, 1, 1)
    assert parsed_calendar[0]["level"] == 1
    assert parsed_calendar[0]["count"] == 1


def test_get_last_year_contributions_shouldupdatedb_whenresponseisok(
    crawler, db_session
):
    with patch("requests.post") as mock_post:
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {
            "data": {
                "user": {
                    "contributionsCollection": {
                        "contributionCalendar": {
                            "weeks": [
                                {
                                    "contributionDays": [
                                        {
                                            "date": "2024-01-01",
                                            "contributionLevel": "FIRST_QUARTILE",
                                            "contributionCount": 1,
                                        },
                                        {
                                            "date": "2024-01-02",
                                            "contributionLevel": "NONE",
                                            "contributionCount": 0,
                                        },
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        }

        crawler.get_last_year_contributions()

        contributions = db_session.query(DBLastYearContributions).all()
        assert len(contributions) == 2
        assert contributions[0].date == datetime(2024, 1, 1)
        assert contributions[0].count == 1
        assert contributions[1].date == datetime(2024, 1, 2)
        assert contributions[1].count == 0


def test_get_last_year_contributions_shouldnotupdatedb_whenresponseisnotok(
    crawler, db_session
):
    with patch.object(
        crawler,
        "_fetch_last_year_contributions",
        side_effect=requests.exceptions.RequestException,
    ):
        db_session.query(DBLastYearContributions).delete()
        crawler.get_last_year_contributions()

        contributions = db_session.query(DBLastYearContributions).all()
        assert len(contributions) == 0


def test__fetch_yearly_contributions_shouldreturncontributions_whenresponseok(crawler):
    with patch("requests.post") as mock_post:
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = {
            "data": {
                "user": {
                    "contributionsCollection": {
                        "restrictedContributionsCount": 50,
                        "contributionCalendar": {
                            "totalContributions": 100,
                        },
                    }
                }
            }
        }

        contributions = crawler._fetch_yearly_contributions(2024)

        assert contributions["restrictedContributionsCount"] == 50
        assert contributions["contributionCalendar"]["totalContributions"] == 100


def test_get_total_contributions_shouldupdatedb_whenresponseisok(crawler, db_session):
    with patch.object(crawler, "_fetch_yearly_contributions") as mock_fetch:
        mock_fetch.return_value = {
            "restrictedContributionsCount": 50,
            "contributionCalendar": {"totalContributions": 100},
        }

        crawler.get_total_contributions()

        contributions = db_session.query(DBTotalContributions).first()
        first_year = 2022
        this_year = datetime.now().year
        number_of_years = this_year - first_year + 1

        assert contributions.total_contributions == 150 * number_of_years


def test_get_total_contributions_shouldnotupdatedb_whenresponseisnotok(
    crawler, db_session
):
    with patch.object(
        crawler,
        "_fetch_yearly_contributions",
        side_effect=requests.exceptions.RequestException,
    ):
        db_session.query(DBTotalContributions).delete()
        crawler.get_total_contributions()

        contributions = db_session.query(DBTotalContributions).all()
        assert len(contributions) == 0


def test__get_repo_languages_shouldreturnlanguages_whenresponseisok(crawler):
    with patch("requests.get") as mock_get:
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = {"Python": 123, "Java": 456}

        languages = crawler._get_repo_languages("repo1")

        assert len(languages) == 2
        assert languages["Python"] == 123
        assert languages["Java"] == 456


def test__get_repo_languages_shouldreturnNone_whenresponseisnotok(crawler):
    with patch("requests.get") as mock_get:
        mock_get.return_value.ok = False

        languages = crawler._get_repo_languages("repo1")

        assert languages is None


def test__parse_languages_shouldreturnlanguages_whenresponseisvalid(crawler):
    languages = {"Python": 123}
    repo_languages = {
        "Python": 123,
        "Java": 456,
    }

    parsed_languages = crawler._parse_languages(languages, repo_languages)

    assert len(parsed_languages) == 2
    assert parsed_languages["Python"] == 246
    assert parsed_languages["Java"] == 456


def test_get_language_usage_shouldupdatedb_whenresponseisok(crawler, db_session):
    with patch.object(crawler, "_get_repo_languages") as mock_get:
        mock_get.return_value = {"Python": 123}

        crawler.repos = ["repo1"]
        crawler.get_language_usage()

        languages = db_session.query(DBLanguageUsage).all()
        assert len(languages) == 1
        assert languages[0].language == "Python"
        assert languages[0].count == 123


def test_get_language_usage_shouldnotupdatedb_whenresponseisnotok(crawler, db_session):
    with patch.object(
        crawler, "_get_repo_languages", side_effect=requests.exceptions.RequestException
    ):
        crawler.repos = ["repo1"]
        crawler.get_language_usage()

        languages = db_session.query(DBLanguageUsage).all()
        assert len(languages) == 0


def test_get_language_usage_shouldreturnNone_wehnnoreposfound(crawler, db_session):
    with patch.object(crawler, "get_repos", return_value=None):
        crawler.repos = []
        result = crawler.get_language_usage()

        assert result is None
        languages = db_session.query(DBLanguageUsage).all()
        assert len(languages) == 0


def test__count_lines_shouldreturnlines_whenresponseisok(crawler):
    mock_file_content = "line1\nline2\nline3\n"
    crawler.total_lines = 0

    with patch("builtins.open", mock_open(read_data=mock_file_content)):
        crawler._count_lines("dummy_path")

    assert crawler.total_lines == 3


def test_get_total_lines_shouldupdatedb_whenresponseisok(crawler, db_session):
    crawler.repos = ["repo1"]
    crawler.total_lines = 0

    with patch("os.path.exists", return_value=True):
        with patch.object(crawler, "_pull_repo"):
            with patch("os.walk") as mock_walk:
                mock_walk.return_value = [
                    ("./repos/repo1", [], ["file1.py"]),
                ]

                with patch(
                    "builtins.open", mock_open(read_data="line1\nline2\nline3\n")
                ):
                    crawler.get_total_lines()

                lines = db_session.query(DBTotalLines).first()
                assert lines.total_lines == 3
