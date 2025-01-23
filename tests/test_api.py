import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session
from api.main import app
from db.core import Base, get_db
from db.models import (
    DBLastYearContributions,
    DBTotalContributions,
    DBLanguageUsage,
    DBTotalLines,
)
from datetime import datetime

client = TestClient(app)

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


def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def run_before_and_after_tests():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="module")
def api_key():
    return os.getenv("API_KEY")


@pytest.fixture()
def mock_last_year_contributions():
    db = TestingSessionLocal()
    db.add_all(
        [
            DBLastYearContributions(date=datetime(2024, 1, 21), count=1, level=1),
            DBLastYearContributions(date=datetime(2024, 1, 22), count=0, level=0),
        ]
    )
    db.commit()
    db.close()


@pytest.fixture()
def mock_total_contributions():
    db = TestingSessionLocal()
    db.add(
        DBTotalContributions(total_contributions=123),
    )
    db.commit()
    db.close()


@pytest.fixture()
def mock_language_usage():
    db = TestingSessionLocal()
    db.add_all(
        [
            DBLanguageUsage(language="Python", count=123),
            DBLanguageUsage(language="Java", count=123),
        ]
    )
    db.commit()
    db.close()


@pytest.fixture()
def mock_total_lines():
    db = TestingSessionLocal()
    db.add(
        DBTotalLines(total_lines=123),
    )
    db.commit()
    db.close()


def test_root_shouldreturn200whenapikeyisok(api_key):
    response = client.get("/", headers={"api-key": api_key})
    assert response.status_code == 200
    assert response.json() == {"message": "Server online"}


def test_root_shouldreturn403whenapikeyiswrong():
    response = client.get("/", headers={"api-key": "wrong_api_key"})
    assert response.status_code == 403
    assert response.json() == {"detail": "Not authenticated"}


def test_root_shouldreturn429whenratelimitisreached(api_key):
    for _ in range(11):
        response = client.get("/", headers={"api-key": api_key})
    assert response.status_code == 429
    data = response.json()
    assert "Rate limit exceeded" in data["error"]


def test_get_last_year_contributions_shouldreturn204whendbisempty(api_key):
    response = client.get("/last_year_contributions", headers={"api-key": api_key})
    assert response.status_code == 204


def test_get_last_year_contributions_shouldreturn200whendbhasdata(
    mock_last_year_contributions, api_key
):
    response = client.get("/last_year_contributions", headers={"api-key": api_key})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["date"] == datetime(2024, 1, 21).isoformat()
    assert data[0]["count"] == 1
    assert data[1]["date"] == datetime(2024, 1, 22).isoformat()
    assert data[1]["count"] == 0


def test_get_total_contributions_shouldreturn204whendbisempty(api_key):
    response = client.get("/total_contributions", headers={"api-key": api_key})
    assert response.status_code == 204


def test_get_total_contributions_shouldreturn200whendbhasdata(
    mock_total_contributions, api_key
):
    response = client.get("/total_contributions", headers={"api-key": api_key})
    assert response.status_code == 200
    data = response.json()
    assert data["total_contributions"] == 123


def test_get_language_usage_shouldreturn204whendbisempty(api_key):
    response = client.get("/language_usage", headers={"api-key": api_key})
    assert response.status_code == 204


def test_get_language_usage_shouldreturn200whendbhasdata(mock_language_usage, api_key):
    response = client.get("/language_usage", headers={"api-key": api_key})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["language"] == "Python"
    assert data[0]["count"] == 123
    assert data[1]["language"] == "Java"
    assert data[1]["count"] == 123


def test_get_total_lines_shouldreturn204whendbisempty(api_key):
    response = client.get("/total_lines", headers={"api-key": api_key})
    assert response.status_code == 204


def test_get_total_lines_shouldreturn200whendbhasdata(mock_total_lines, api_key):
    response = client.get("/total_lines", headers={"api-key": api_key})
    assert response.status_code == 200
    data = response.json()
    assert data["total_lines"] == 123
