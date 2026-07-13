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

        delete_john_body = request(
            client,
            "DELETE",
            BASE_URL,
            f"/farmers/1",
            expected_status=204,
        )

        # request(
        #     client,
        #     "GET",
        #     BASE_URL,
        #     "/health",
        #     expected_status=200,
        # )

        # mary_body = request(
        #     client,
        #     "POST",
        #     BASE_URL,
        #     "/farmers",
        #     expected_status=201,
        #     json=FarmerCreate(
        #         name="Mary Farmer",
        #         email=f"mary.{run_id}@example.com",
        #     ),
        # )
        # mary = FarmerRead.model_validate(mary_body)

        # john_body = request(
        #     client,
        #     "POST",
        #     BASE_URL,
        #     "/farmers",
        #     expected_status=201,
        #     json=FarmerCreate(
        #         name="John Farmer",
        #         email=f"john.{run_id}@example.com",
        #     ),
        # )
        # john = FarmerRead.model_validate(john_body)

        # request(
        #     client,
        #     "POST",
        #     BASE_URL,
        #     "/farmers",
        #     expected_status=409,
        #     json=FarmerCreate(
        #         name="Duplicate Mary",
        #         email=mary.email,
        #     ),
        # )

        # daisy_body = request(
        #     client,
        #     "POST",
        #     BASE_URL,
        #     "/cows",
        #     expected_status=201,
        #     json=CowCreate(
        #         tag_number=f"UK-DEMO-{run_id}",
        #         name="Daisy",
        #         breed="Angus",
        #         date_of_birth="2024-04-01",
        #         farmer_id=1,
        #     ),
        # )
        # daisy = CowRead.model_validate(daisy_body)

        # buttercup_body = request(
        #     client,
        #     "POST",
        #     BASE_URL,
        #     "/cows",
        #     expected_status=201,
        #     json=CowCreate(
        #         tag_number=f"UK-JOHN-{run_id}",
        #         name="Buttercup",
        #         breed="Hereford",
        #         date_of_birth="2023-08-15",
        #         farmer_id=john.id,
        #     ),
        # )
        # buttercup = CowRead.model_validate(buttercup_body)

        # request(
        #     client,
        #     "POST",
        #     BASE_URL,
        #     "/cows",
        #     expected_status=409,
        #     json=CowCreate(
        #         tag_number=daisy.tag_number,
        #         name="Duplicate Daisy",
        #         breed="Angus",
        #         date_of_birth="2024-04-01",
        #         farmer_id=mary.id,
        #     ),
        # )

        # same_tag_different_farmer_body = request(
        #     client,
        #     "POST",
        #     BASE_URL,
        #     "/cows",
        #     expected_status=201,
        #     json=CowCreate(
        #         tag_number=daisy.tag_number,
        #         name="Same Tag Different Farm",
        #         breed="Angus",
        #         date_of_birth="2024-05-01",
        #         farmer_id=john.id,
        #     ),
        # )
        # same_tag_different_farmer = CowRead.model_validate(same_tag_different_farmer_body)

        # farmers_body = request(
        #     client,
        #     "GET",
        #     BASE_URL,
        #     "/farmers",
        #     expected_status=200,
        # )
        # farmers = [FarmerRead.model_validate(item) for item in farmers_body]

        # mary_details_body = request(
        #     client,
        #     "GET",
        #     BASE_URL,
        #     f"/farmers/{mary.id}",
        #     expected_status=200,
        # )
        # mary_details = FarmerDetails.model_validate(mary_details_body)

        # cows_body = request(
        #     client,
        #     "GET",
        #     BASE_URL,
        #     "/cows",
        #     expected_status=200,
        # )
        # cows = [CowRead.model_validate(item) for item in cows_body]

        # cows_for_mary_body = request(
        #     client,
        #     "GET",
        #     BASE_URL,
        #     "/cows",
        #     expected_status=200,
        #     params={"farmer_id": mary.id},
        # )
        # cows_for_mary = [CowRead.model_validate(item) for item in cows_for_mary_body]

        # first_measurement_body = request(
        #     client,
        #     "POST",
        #     BASE_URL,
        #     "/measurements",
        #     expected_status=201,
        #     json=MeasurementCreate(
        #         cow_id=1,
        #         recorded_at=datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc),
        #         weight_kg=412.5,
        #         height_cm=122.0,
        #         heart_girth_cm=180.0,
        #         body_condition_score=3.5,
        #         notes="Initial manual demo measurement",
        #     ),
        # )
        # first_measurement = MeasurementRead.model_validate(first_measurement_body)

        # second_measurement_body = request(
        #     client,
        #     "POST",
        #     BASE_URL,
        #     "/measurements",
        #     expected_status=201,
        #     json=MeasurementCreate(
        #         cow_id=daisy.id,
        #         recorded_at=datetime(2026, 7, 11, 12, 0, tzinfo=timezone.utc),
        #         weight_kg=430.0,
        #         height_cm=123.0,
        #         heart_girth_cm=183.0,
        #         body_condition_score=3.75,
        #         notes="Follow-up manual demo measurement",
        #     ),
        # )
        # second_measurement = MeasurementRead.model_validate(second_measurement_body)

        # request(
        #     client,
        #     "POST",
        #     BASE_URL,
        #     "/measurements",
        #     expected_status=404,
        #     json=MeasurementCreate(
        #         cow_id=999999,
        #         recorded_at=datetime(2026, 7, 12, 12, 0, tzinfo=timezone.utc),
        #         weight_kg=400.0,
        #     ),
        # )

        # # This intentionally uses a raw dict to prove the API rejects it
        # request(
        #     client,
        #     "POST",
        #     BASE_URL,
        #     "/measurements",
        #     expected_status=422,
        #     json={
        #         "cowId": daisy.id,
        #         "recordedAt": "2026-07-12T12:00:00Z",
        #         "notes": "This should fail because there is no measurement value",
        #     },
        # )

        # daisy_measurements_body = request(
        #     client,
        #     "GET",
        #     BASE_URL,
        #     "/measurements",
        #     expected_status=200,
        #     params={"cowId": daisy.id},
        # )
        # daisy_measurements = [
        #     MeasurementRead.model_validate(item)
        #     for item in daisy_measurements_body
        # ]

        # daisy_details_body = request(
        #     client,
        #     "GET",
        #     BASE_URL,
        #     f"/cows/{daisy.id}",
        #     expected_status=200,
        # )
        # daisy_details = CowDetails.model_validate(daisy_details_body)

        # print()
        # print("Typed objects created from API responses:")
        # print(f"Mary farmer id: {mary.id}")
        # print(f"John farmer id: {john.id}")
        # print(f"Daisy cow id: {daisy.id}")
        # print(f"Buttercup cow id: {buttercup.id}")
        # print(f"Same-tag different-farmer cow id: {same_tag_different_farmer.id}")
        # print(f"First measurement id: {first_measurement.id}")
        # print(f"Second measurement id: {second_measurement.id}")

        # print()
        # print("Validated workflow summary:")
        # print(f"Total farmers returned: {len(farmers)}")
        # print(f"Mary's cows from farmer detail: {len(mary_details.cows)}")
        # print(f"Total cows returned: {len(cows)}")
        # print(f"Cows for Mary: {len(cows_for_mary)}")
        # print(f"Measurements for Daisy: {len(daisy_measurements)}")
        # print(f"Measurements inside Daisy detail: {len(daisy_details.measurements)}")


if __name__ == "__main__":
    main()
