from collections.abc import Iterator
from datetime import date, datetime, timezone
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.routes.farmers import router as farmers_router
from app.db import get_db
from app.models import CowMeasurementModel, CowModel, FarmerModel


def make_farmer(farmer_id: int = 1, name: str = "John Doe", email: str = "john@test.com") -> FarmerModel:
    farmer = FarmerModel(
        name=name,
        email=email,
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

@pytest.fixture
def db() -> MagicMock:
    return MagicMock(spec=Session)


@pytest.fixture
def client(db: MagicMock) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(farmers_router, prefix="/farmers")

    def override_get_db() -> Iterator[MagicMock]:
        yield db
    
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

def test_create_farmer_success(client: TestClient, db: MagicMock) -> None:

    def refresh_created_farmer(farmer: FarmerModel) -> None:
        farmer.id = 1
    
    db.refresh.side_effect = refresh_created_farmer

    response = client.post(
        "/farmers",
        json={
            "name": "John Doe",
            "email": "john@test.com",
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "John Doe"
    assert body["email"] == "john@test.com"

    db.add.assert_called_once()
    created_farmer = db.add.call_args.args[0]
    assert isinstance(created_farmer, FarmerModel)
    assert created_farmer.name == "John Doe"
    assert created_farmer.email == "john@test.com"

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(created_farmer)
    db.rollback.assert_not_called()

def test_create_farmer_rejects_invalid_email(
    client: TestClient,
    db: MagicMock,
) -> None:
    response = client.post(
        "/farmers",
        json={
            "name": "John Doe",
            "email": "not-an-email",
        },
    )

    assert response.status_code == 422

    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()
    db.rollback.assert_not_called()


def test_create_farmer_rejects_extra_fields(
    client: TestClient,
    db: MagicMock,
) -> None:
    response = client.post(
        "/farmers",
        json={
            "name": "John Doe",
            "email": "john@test.com",
            "unexpectedField": "should not be accepted",
        },
    )

    assert response.status_code == 422

    db.add.assert_not_called()
    db.commit.assert_not_called()
    db.refresh.assert_not_called()
    db.rollback.assert_not_called()


def test_create_farmer_returns_409_when_email_already_exists(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.commit.side_effect = IntegrityError(
        statement="INSERT INTO farmers ...",
        params={},
        orig=Exception("duplicate email"),
    )

    response = client.post(
        "/farmers",
        json={
            "name": "John Doe",
            "email": "john@test.com",
        },
    )

    assert response.status_code == 409
    assert response.json() == {"detail": "Farmer email already exists"}

    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.rollback.assert_called_once()
    db.refresh.assert_not_called()


def test_list_farmers_success(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.scalars.return_value = [
        make_farmer(
            farmer_id=1,
            name="John Doe",
            email="john@test.com",
        ),
        make_farmer(
            farmer_id=2,
            name="John Farmer",
            email="john@test.com",
        ),
    ]

    response = client.get("/farmers?limit=50&offset=0")

    assert response.status_code == 200

    body = response.json()
    assert len(body) == 2

    assert body[0]["id"] == 1
    assert body[0]["name"] == "John Doe"
    assert body[0]["email"] == "john@test.com"

    assert body[1]["id"] == 2
    assert body[1]["name"] == "John Farmer"
    assert body[1]["email"] == "john@test.com"

    db.scalars.assert_called_once()


def test_list_farmers_returns_empty_list_when_no_farmers_exist(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.scalars.return_value = []

    response = client.get("/farmers")

    assert response.status_code == 200
    assert response.json() == []

    db.scalars.assert_called_once()


def test_get_farmer_success_includes_cows(
    client: TestClient,
    db: MagicMock,
) -> None:
    farmer = make_farmer(
        farmer_id=1,
        name="John Doe",
        email="john@test.com",
    )
    farmer.cows = [
        make_cow(
            cow_id=10,
            farmer_id=1,
            tag_number="COWTAG1",
        )
    ]

    db.scalar.return_value = farmer

    response = client.get("/farmers/1")

    assert response.status_code == 200

    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "John Doe"
    assert body["email"] == "john@test.com"

    assert len(body["cows"]) == 1
    assert body["cows"][0]["id"] == 10
    assert body["cows"][0]["tagNumber"] == "COWTAG1"
    assert body["cows"][0]["cowName"] == "John Cow"
    assert body["cows"][0]["breed"] == "Hungarian Grey"
    assert body["cows"][0]["dateOfBirth"] == "2023-01-01"
    assert body["cows"][0]["farmerId"] == 1
    assert body["cows"][0]["ageDays"] >= 0

    db.scalar.assert_called_once()


def test_get_farmer_returns_404_when_farmer_does_not_exist(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.scalar.return_value = None

    response = client.get("/farmers/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Farmer not found"}

    db.scalar.assert_called_once()


def test_get_farmer_rejects_non_integer_farmer_id(
    client: TestClient,
    db: MagicMock,
) -> None:
    response = client.get("/farmers/not-an-id")

    assert response.status_code == 422

    db.scalar.assert_not_called()


def test_delete_farmer_success(
    client: TestClient,
    db: MagicMock,
) -> None:
    farmer = make_farmer(farmer_id=1)
    db.get.return_value = farmer

    response = client.delete("/farmers/1")

    assert response.status_code == 204
    assert response.content == b""

    db.get.assert_called_once_with(FarmerModel, 1)
    db.delete.assert_called_once_with(farmer)
    db.commit.assert_called_once()
    db.rollback.assert_not_called()


def test_delete_farmer_returns_404_when_farmer_does_not_exist(
    client: TestClient,
    db: MagicMock,
) -> None:
    db.get.return_value = None

    response = client.delete("/farmers/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Farmer not found"}

    db.get.assert_called_once_with(FarmerModel, 999)
    db.delete.assert_not_called()
    db.commit.assert_not_called()
    db.rollback.assert_not_called()


def test_delete_farmer_rolls_back_when_database_rejects_delete(
    client: TestClient,
    db: MagicMock,
) -> None:
    farmer = make_farmer(farmer_id=1)
    db.get.return_value = farmer
    db.commit.side_effect = IntegrityError(
        statement="DELETE FROM farmers ...",
        params={},
        orig=Exception("database error"),
    )

    response = client.delete("/farmers/1")

    assert response.status_code == 400
    assert response.json() == {"detail": "Farmer could not be deleted"}

    db.get.assert_called_once_with(FarmerModel, 1)
    db.delete.assert_called_once_with(farmer)
    db.commit.assert_called_once()
    db.rollback.assert_called_once()

