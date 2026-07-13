from collections.abc import Iterator
from datetime import date, datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.routes.cows import router as cows_router
from app.db import get_db
from app.models import CowMeasurementModel, CowModel, FarmerModel


def make_farmer(farmer_id: int = 1) -> FarmerModel:
    farmer = FarmerModel(
        name="John Doe",
        email="john@test.com",
    )
    farmer.id=farmer_id
    return farmer

def make_cow(
    cow_id: int = 1,
    farmer_id: int = 1,
    tag_number: str = "COWTAG1"
) -> CowModel:
    cow = CowModel(
        tag_number=tag_number,
        name="John Cow",
        breed="Hungarian Grey",
        date_of_birth=date(2023, 1, 1),
        farmer_id=farmer_id
    )
    cow.id= cow_id
    cow.measurements = []
    return cow

def make_measurement(
    measurement_id: int = 10,
    cow_id: int = 1,
) -> CowMeasurementModel:
    measurement = CowMeasurementModel(
        cow_id=cow_id,
        recorded_at=datetime(2026, 7, 9, 12, 0, tzinfo=timezone.utc),
        weight_kg=400.5,
        height_cm=120.0,
        heart_girth_cm=180.0,
        body_condition_score=3.5,
        notes="Good fella",
    )
    measurement.id = measurement_id
    return measurement

# Fake DB
@pytest.fixture
def db() -> MagicMock:
    return MagicMock(spec=Session)


#Real small test only app, with the cow router mounted to it
@pytest.fixture
def client(db: MagicMock) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(cows_router, prefix="/cows")

    def override_get_db() -> Iterator[MagicMock]:
        yield db
    
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_cow_success(client: TestClient, db: MagicMock) -> None:
    db.get.return_value = make_farmer()

    def refresh_created_cow(cow: CowModel) -> None:
        cow.id = 1

    db.refresh.side_effect = refresh_created_cow

    response = client.post(
        "/cows",
        json={
            "tagNumber": "COWTAG1",
            "cowName": "John Cow",
            "breed": "Hungarian Grey",
            "dateOfBirth": "2023-01-01",
            "farmerId": 1,
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["id"] == 1
    assert body["tagNumber"] == "COWTAG1"
    assert body["cowName"] == "John Cow"
    assert body["breed"] == "Hungarian Grey"
    assert body["dateOfBirth"] == "2023-01-01"
    assert body["farmerId"] == 1
    assert body["ageDays"] >= 0

    db.get.assert_called_once_with(FarmerModel, 1)
    db.add.assert_called_once()

    created_cow = db.add.call_args.args[0]
    assert isinstance(created_cow, CowModel)
    assert created_cow.tag_number == "COWTAG1"
    assert created_cow.name == "John Cow"
    assert created_cow.breed == "Hungarian Grey"
    assert created_cow.farmer_id == 1

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(created_cow)

def test_create_cow_returns_404_when_farmer_does_not_exist(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.get.return_value = None

    response = client.post(
        "/cows",
        json={
            "tagNumber": "COWTAG1",
            "cowName": "John Cow",
            "breed": "Hungarian Grey",
            "dateOfBirth": "2023-01-01",
            "farmerId": 999,
        },
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Farmer not found"}

    db.get.assert_called_once_with(FarmerModel, 999)
    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()


def test_create_cow_returns_409_when_unique_constraint_fails(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.get.return_value = make_farmer()
    db.commit.side_effect = IntegrityError(
        statement="INSERT INTO cows ...",
        params={},
        orig=Exception("duplicate cow tag"),
    )

    response = client.post(
        "/cows",
        json={
            "tagNumber": "COWTAG1",
            "cowName": "John Cow",
            "breed": "Hungarian Grey",
            "dateOfBirth": "2023-01-01",
            "farmerId": 1,
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Cow already exists for this farmer"}

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.rollback.assert_called_once()
    db.refresh.assert_not_called()


def test_list_cows_success(client: TestClient, db: MagicMock) -> None:
    db.scalars.return_value = [make_cow()]

    response = client.get("/cows?farmer_id=1&limit=50&offset=0")

    assert response.status_code == 200

    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == 1
    assert body[0]["tagNumber"] == "COWTAG1"
    assert body[0]["farmerId"] == 1

    db.scalars.assert_called_once()


def test_get_cow_success_includes_measurements(
    client: TestClient,
    db: MagicMock,
) -> None:
    cow = make_cow()
    cow.measurements = [make_measurement()]
    db.scalar.return_value = cow

    response = client.get("/cows/1")

    assert response.status_code == 200

    body = response.json()
    assert body["id"] == 1
    assert body["tagNumber"] == "COWTAG1"
    assert len(body["measurements"]) == 1
    assert body["measurements"][0]["cowId"] == 1
    assert body["measurements"][0]["weightKg"] == 400.5
    assert body["measurements"][0]["heightCm"] == 120.0
    assert body["measurements"][0]["heartGirthCm"] == 180.0
    assert body["measurements"][0]["bodyConditionScore"] == 3.5


def test_get_cow_returns_404_when_missing(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.scalar.return_value = None

    response = client.get("/cows/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Cow not found"}

    db.scalar.assert_called_once()

def test_create_cow_rejects_extra_fields(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.get.return_value = make_farmer()

    def refresh_created_cow(cow: CowModel) -> None:
        cow.id = 1

    db.refresh.side_effect = refresh_created_cow

    response = client.post(
        "/cows",
        json={
            "tagNumber": "COWTAG1",
            "cowName": "John Cow",
            "breed": "Hungarian Grey",
            "dateOfBirth": "2023-01-01",
            "farmerId": 1,
            "unexpectedField": "should not be accepted",
        },
    )

    assert response.status_code == 422

    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()
    db.rollback.assert_not_called()

def test_create_cow_rejects_invalid_tag_number(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.get.return_value = make_farmer()

    def refresh_created_cow(cow: CowModel) -> None:
        cow.id = 1

    db.refresh.side_effect = refresh_created_cow

    response = client.post(
        "/cows",
        json={
            "tagNumber": 1,
            "cowName": "John Cow",
            "breed": "Hungarian Grey",
            "dateOfBirth": "2023-01-01",
            "farmerId": 1,
        },
    )

    assert response.status_code == 422

    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()
    db.rollback.assert_not_called()


def test_delete_cow_success(
    client: TestClient,
    db: MagicMock,
) -> None:
    cow = make_cow(cow_id=1)
    db.get.return_value = cow

    response = client.delete("/cows/1")

    assert response.status_code == 204
    assert response.content == b""

    db.get.assert_called_once_with(CowModel, 1)
    db.delete.assert_called_once_with(cow)
    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_delete_cow_returns_404_when_cow_does_not_exist(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.get.return_value = None

    response = client.delete("/cows/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Cow not found"}

    db.get.assert_called_once_with(CowModel, 999)
    db.delete.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_delete_cow_rolls_back_when_database_rejects_delete(
    client: TestClient,
    db: MagicMock,
) -> None:
    cow = make_cow(cow_id=1)
    db.get.return_value = cow
    db.commit.side_effect = IntegrityError(
        statement="DELETE FROM cows ...",
        params={},
        orig=Exception("database error"),
    )

    response = client.delete("/cows/1")

    assert response.status_code == 400
    assert response.json() == {"detail": "Cow could not be deleted"}

    db.get.assert_called_once_with(CowModel, 1)
    db.delete.assert_called_once_with(cow)
    db.commit.assert_called_once()
    db.rollback.assert_called_once()
