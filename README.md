# Breedr_interview_project
Second stage interview with breedr
Using FastAPI for web framework because I know how to use it
Pydantic for request and response validation
SQLAlchemy as the ORM as it integrates well with FastAPI
pytest for testing
ruff for linting

Tables in DB:
Farmers - List of farmers, each farmer can have many cows
Cows - List of cows, each cow has one farmer, each cow has many measurements
Cow Measurements - Cow measurements, updated each time a cow is measured, a cow will have multiple measurements


<Possible API Requests:>
Create Farmer,
Get Farmers,
Get certain Farmer,
Delete Farmer

Create Cow,
Get list of cows(every cow or a particular farmers cows)
Get certain cow,
Delete Cow

Create Measurement,
Get measurements for a certain cow
Delete Measurement


<What I would change if I wanted to make this real(small changes if I had more time):>
Change primairy keys to UUID
Change SQLite to PostgreSQL to handle more data, plus async writes
Alembic migration to have version control
Add medicine db table, and events db table, both acting the same way as measurements acts, as a historic table
Make frontend for sending API requests
Add more animals
Add PATCH requests
Add CSV import for large cow onboardings

<What I would change if I wanted to make this real(actual product sorta changes):>
Change to Django
Change to GraphQL
Host app on AWS Lambdas
RDS for PostgreSQL
Add authentication for Users and Farms
Soft Deletes, maybe using Glacier
Logging, Cloudwatch for monitoring
Report generation

Figure out bad connectivity stuff:
    Store changes locally on devices when not connected, 
    when connected apply changes from all devices based on timestamp,
    Manualy sort out conflicts(job of farm administrator)



"Unit tests" use FastAPI's real request handling and pydantic validations
But they replacethe SQLAlchemy session with a mock

<To run unit tests:>
uv run pytest tests/app/api/routes/test_cows.py
uv run pytest tests/app/api/routes/test_measurements.py
uv run pytest tests/app/api/routes/test_farmers.py

<run "end to end":>
uv run python -m tests.manual_API_requests.end_to_end.total_workflow_test

<To run app:>
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

<Reset DB:>
uv run python -m tests.manual_API_requests.reset_db

<run manual requests:>
uv run python -m tests.manual_API_requests.run_requests

Example requests:

*FARMERS*
Create a farmer:
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

Get farmers list:
farmers_body = request(
            client,
            "GET",
            BASE_URL,
            "/farmers",
            expected_status=200,
        )

Get specific farmer details:
john_details_body = request(
            client,
            "GET",
            BASE_URL,
            f"/farmers/*JOHN_ID*",
            expected_status=200,
        )

Delete farmer:
delete_john_body = request(
            client,
            "DELETE",
            BASE_URL,
            f"/farmers/*JOHN_ID*",
            expected_status=204,
        )


*COWS*
Create a cow:
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
                farmer_id=1,
            ),
        )

Get cows list:
cows_body = request(
            client,
            "GET",
            BASE_URL,
            "/cows",
            expected_status=200,
        )

Get cows of farmer:
cows_for_john_body = request(
            client,
            "GET",
            BASE_URL,
            "/cows",
            expected_status=200,
            params={"farmer_id": *JOHN_ID*},
        )

Get certain cow:
burger_cow_body = request(
            client,
            "GET",
            BASE_URL,
            f"/cows/*BURGER_ID*",
            expected_status=200,
        )

Delete cow:
delete_cow_body = request(
        client,
        "DELETE",
        BASE_URL,
        f"/cows/*BURGER_ID*",
        expected_status=204,
    )


*MEASURMENTS*
Create measurement:
first_measurement_body = request(
            client,
            "POST",
            BASE_URL,
            "/measurements",
            expected_status=201,
            json=MeasurementCreate(
                cow_id=*BURGER_ID*,
                recorded_at=datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc),
                weight_kg=412.5,
                height_cm=122.0,
                heart_girth_cm=180.0,
                body_condition_score=3.5,
                notes="Initial manual demo measurement",
            ),
        )

Get measurement for certain Cow:
burger_measurements_body = request(
            client,
            "GET",
            BASE_URL,
            "/measurements",
            expected_status=200,
            params={"cowId": *BURGER_ID*},
        )

Delete measurement:
delete_measurement_body = request(
        client,
        "DELETE",
        BASE_URL,
        f"/measurements/*MEASUREMENT_ID*",
        expected_status=204,
    )






Kill port in powershell:

Get-NetTCPConnection -LocalPort 8000 | Select-Object LocalAddress,LocalPort,State,OwningProcess
Get-Process -Id <OwningProcessValue>
Stop-Process -Id <OwningProcessValue> -Force

