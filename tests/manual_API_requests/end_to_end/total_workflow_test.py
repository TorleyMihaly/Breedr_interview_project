from __future__ import annotations

import os
import time
from datetime import datetime, timezone

import httpx

#from app.schemas import FarmerCreate, FarmerRead
from tests.manual_API_requests.client_helpers import request
from app.schemas import (
    CowCreate,
    CowDetails,
    CowRead,
    FarmerCreate,
    FarmerDetails,
    FarmerRead,
    MeasurementCreate,
    MeasurementRead,
)



BASE_URL = os.getenv("BREEDR_API_URL", "http://127.0.0.1:8000")


def main() -> None:
    run_id = int(time.time())

    with httpx.Client(timeout=10.0) as client:
        print(f"Sending real HTTP requests to {BASE_URL}")

        request(
            client,
            "GET",
            BASE_URL,
            "/health",
            expected_status=200,
        )

        john_body = request(
            client,
            "POST",
            BASE_URL,
            "/farmers",
            expected_status=201,
            json=FarmerCreate(
                name="John Farmer",
                email=f"john.{run_id}@example.com",
            ),
        )
        john = FarmerRead.model_validate(john_body)

        burger_body = request(
            client,
            "POST",
            BASE_URL,
            "/cows",
            expected_status=201,
            json=CowCreate(
                tag_number=f"UK-DEMO-{run_id}",
                name="Burger",
                breed="Angus",
                date_of_birth="2024-04-01",
                farmer_id=john.id,
            ),
        )
        burger = CowRead.model_validate(burger_body)

        first_measurement_body = request(
            client,
            "POST",
            BASE_URL,
            "/measurements",
            expected_status=201,
            json=MeasurementCreate(
                cow_id=burger.id,
                recorded_at=datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc),
                weight_kg=412.5,
                height_cm=122.0,
                heart_girth_cm=180.0,
                body_condition_score=3.5,
                notes="Initial manual demo measurement",
            ),
        )
        measurement_1 = MeasurementRead.model_validate(first_measurement_body)

        john_details_body = request(
            client,
            "GET",
            BASE_URL,
            f"/farmers/{john.id}",
            expected_status=200,
        )

        cows_for_john_body = request(
            client,
            "GET",
            BASE_URL,
            "/cows",
            expected_status=200,
            params={"farmer_id": john.id},
        )

        burger_measurements_body = request(
            client,
            "GET",
            BASE_URL,
            "/measurements",
            expected_status=200,
            params={"cowId": burger.id},
        )

        print("Proceed with delete Y/N?\n")
        answer = input()
        if answer == "N":
            return
        
        delete_john_body = request(
            client,
            "DELETE",
            BASE_URL,
            f"/farmers/{john.id}",
            expected_status=204,
        )


if __name__ == "__main__":
    main()
