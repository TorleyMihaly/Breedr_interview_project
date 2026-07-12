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


Possible API Requests:
Create Farmer,
Get Farmer details,
Get Farmers,
Create Cow,



What I would change if I wanted to make this real:
Change primary keys to UUID
Alembic migration
Add medicine db table, and events db table, both acting the same way as measurements acts, as a historic table



To run unit tests:
uv run pytest tests/app/api/routes/test_cows.py
uv run pytest tests/app/api/routes/test_measurements.py
uv run pytest tests/app/api/routes/test_farmers.py