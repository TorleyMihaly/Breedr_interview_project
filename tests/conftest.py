from collections.abc import Callable, Generator
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import get_db
from app.main import create_app
from app.models import Base


@pytest.fixture
def test_engine() -> Generator[Engine, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)

    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def test_session_factory(test_engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=test_engine,
        autoflush=False,
        expire_on_commit=False,
    )


@pytest.fixture
def app(test_session_factory: sessionmaker[Session]) -> Generator[FastAPI, None, None]:
    test_app = create_app(create_tables=False)

    def override_get_db() -> Generator[Session, None, None]:
        with test_session_factory() as db:
            yield db

    test_app.dependency_overrides[get_db] = override_get_db

    try:
        yield test_app
    finally:
        test_app.dependency_overrides.clear()


@pytest.fixture
def api_client(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client


@pytest.fixture
def assert_response() -> Callable[[Response, int], Any]:
    def _assert_response(response: Response, expected_status_code: int) -> Any:
        assert response.status_code == expected_status_code, response.text

        if not response.content:
            return None

        return response.json()

    return _assert_response