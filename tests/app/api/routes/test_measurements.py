from collections.abc import Iterator
from datetime import date, datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.routes.measurements import router as measurements_router
from app.db import get_db
from app.models import CowMeasurementModel, CowModel


def make_cow(
    cow_id: int = 1,
    farmer_id: int = 1,
    tag_number: str = "COWTAG1",
) -> CowModel:
    cow = CowModel(
        tag_number=tag_number,
        name="John Cow",
        breed="Hungarian Grey",
        date_of_birth=date(2024, 4, 1),
        farmer_id=farmer_id,
    )
    cow.id = cow_id
    cow.measurements = []
    return cow


def make_measurement(
    measurement_id: int = 10,
    cow_id: int = 1,
) -> CowMeasurementModel:
    measurement = CowMeasurementModel(
        cow_id=cow_id,
        recorded_at=datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc),
        weight_kg=412.5,
        height_cm=122.0,
        heart_girth_cm=180.0,
        body_condition_score=3.5,
        notes="Good fella",
    )
    measurement.id = measurement_id
    return measurement


@pytest.fixture
def db() -> MagicMock:
    return MagicMock(spec=Session)


@pytest.fixture
def client(db: MagicMock) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(measurements_router, prefix="/measurements")

    def override_get_db() -> Iterator[MagicMock]:
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_measurement_success_uses_cow_id_from_payload(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.get.return_value = make_cow(cow_id=1)

    def refresh_created_measurement(measurement: CowMeasurementModel) -> None:
        measurement.id = 10

    db.refresh.side_effect = refresh_created_measurement

    response = client.post(
        "/measurements",
        json={
            "cowId": 1,
            "recordedAt": "2026-07-10T12:00:00Z",
            "weightKg": 412.5,
            "heightCm": 122.0,
            "heartGirthCm": 180.0,
            "bodyConditionScore": 3.5,
            "notes": "Good fella",
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["id"] == 10
    assert body["cowId"] == 1
    assert body["recordedAt"] == "2026-07-10T12:00:00Z"
    assert body["weightKg"] == 412.5
    assert body["heightCm"] == 122.0
    assert body["heartGirthCm"] == 180.0
    assert body["bodyConditionScore"] == 3.5
    assert body["notes"] == "Good fella"

    db.get.assert_called_once_with(CowModel, 1)
    db.add.assert_called_once()

    created_measurement = db.add.call_args.args[0]
    assert isinstance(created_measurement, CowMeasurementModel)
    assert created_measurement.cow_id == 1
    assert created_measurement.weight_kg == 412.5
    assert created_measurement.height_cm == 122.0
    assert created_measurement.heart_girth_cm == 180.0
    assert created_measurement.body_condition_score == 3.5

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(created_measurement)


def test_create_measurement_returns_404_when_cow_does_not_exist(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.get.return_value = None

    response = client.post(
        "/measurements",
        json={
            "cowId": 999,
            "recordedAt": "2026-07-10T12:00:00Z",
            "weightKg": 412.5,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Cow not found"}

    db.get.assert_called_once_with(CowModel, 999)
    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_create_measurement_rolls_back_when_database_rejects_insert(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.get.return_value = make_cow(cow_id=1)
    db.commit.side_effect = IntegrityError(
        statement="INSERT INTO cow_measurements ...",
        params={},
        orig=Exception("database error"),
    )

    response = client.post(
        "/measurements",
        json={
            "cowId": 1,
            "recordedAt": "2026-07-10T12:00:00Z",
            "weightKg": 412.5,
        },
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Could not create measurement"}

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.rollback.assert_called_once()
    db.refresh.assert_not_called()


def test_create_measurement_rejects_body_without_measurement_values(
    client: TestClient,
    db: MagicMock,
) -> None:
    response = client.post(
        "/measurements",
        json={
            "cowId": 1,
            "recordedAt": "2026-07-10T12:00:00Z",
            "notes": "No actual measurement values",
        },
    )

    assert response.status_code == 422

    db.get.assert_not_called()
    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_get_measurements_success_uses_cow_id_query_parameter(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.get.return_value = make_cow(cow_id=1)
    db.scalars.return_value = [make_measurement(cow_id=1)]

    response = client.get("/measurements?cowId=1")

    assert response.status_code == 200

    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == 10
    assert body[0]["cowId"] == 1
    assert body[0]["recordedAt"] == "2026-07-10T12:00:00Z"
    assert body[0]["weightKg"] == 412.5
    assert body[0]["heightCm"] == 122.0
    assert body[0]["heartGirthCm"] == 180.0
    assert body[0]["bodyConditionScore"] == 3.5
    assert body[0]["notes"] == "Good fella"

    db.get.assert_called_once_with(CowModel, 1)
    db.scalars.assert_called_once()


def test_get_measurements_returns_404_when_cow_does_not_exist(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.get.return_value = None

    response = client.get("/measurements?cowId=999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Cow not found"}

    db.get.assert_called_once_with(CowModel, 999)
    db.scalars.assert_not_called()


def test_get_measurements_requires_cow_id_query_parameter(
    client: TestClient,
    db: MagicMock,
) -> None:
    response = client.get("/measurements")

    assert response.status_code == 422

    db.get.assert_not_called()
    db.scalars.assert_not_called()
