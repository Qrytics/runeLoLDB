"""Shared test fixtures for RuneLoLDB backend tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
# Import all models so they are registered with Base.metadata before table creation
import app.models  # noqa: F401
from main import app

# ---------------------------------------------------------------------------
# Shared in-memory SQLite database for tests (no PostgreSQL required).
# Using the same connection for every session ensures the schema created by
# `create_all` is visible to all test code.
# ---------------------------------------------------------------------------

SQLITE_URL = "sqlite://"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
)

# Keep a single persistent connection so the in-memory database is shared
# across all sessions used during a test.
_connection = engine.connect()


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=_connection)
    yield
    Base.metadata.drop_all(bind=_connection)


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=_connection,
)


@pytest.fixture(scope="function")
def db():
    """Yield a database session for direct model access in tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db):
    """Return a FastAPI TestClient wired to the shared in-memory DB."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Sample rune page fixture
# ---------------------------------------------------------------------------

SAMPLE_RUNE_PAGE = {
    "primaryPath": {
        "id": 8000,
        "name": "Precision",
        "keystone": {"id": 8010, "name": "Conqueror"},
        "slots": [
            {"id": 9111, "name": "Triumph"},
            {"id": 9104, "name": "Legend: Alacrity"},
            {"id": 8014, "name": "Last Stand"},
        ],
    },
    "secondaryPath": {
        "id": 8400,
        "name": "Resolve",
        "slots": [
            {"id": 8429, "name": "Bone Plating"},
            {"id": 8451, "name": "Overgrowth"},
        ],
    },
    "statShards": [
        {"id": 5008, "name": "Adaptive Force"},
        {"id": 5008, "name": "Adaptive Force"},
        {"id": 5002, "name": "Armor"},
    ],
}
