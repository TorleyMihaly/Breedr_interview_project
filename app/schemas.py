from datetime import date, datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from helpers.global_restrictions import email_length, tag_number_length, cow_name_length, cow_breed_length, measurements_notes_length

API_CONFIG = ConfigDict(
    extra="forbid", 
    validate_by_name=True,
    validate_by_alias=True,
)

ORM_CONFIG = ConfigDict(
    extra="forbid", 
    validate_by_name=True,
    validate_by_alias=True,
    from_attributes=True,
)

class FarmerCreate(BaseModel):
    model_config = API_CONFIG

    name: str = Field(
        min_length=1,
        strict=True
    )

    email: str = Field(
        pattern=r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,7}",
        strict=True,
        max_length=email_length
    )

class FarmerRead(FarmerCreate):
    id: int

    model_config = ORM_CONFIG



class CowCreate(BaseModel):
    model_config = API_CONFIG

    tag_number: str = Field(
        alias="tagNumber",
        min_length=1,
        max_length=tag_number_length,
        strict=True
    )

    name: str | None = Field(
        alias="cowName",
        default=None,
        max_length=cow_name_length
    )

    breed: str | None = Field(
        alias="breed",
        default=None,
        max_length=cow_breed_length
    )

    date_of_birth: date = Field(
        alias="dateOfBirth"
    )

    farmer_id: int = Field(
        alias="farmerId",
        gt=0
    )

class CowRead(CowCreate):
    id: int
    age_days: int = Field(
        alias="ageDays"
    )

    model_config = ConfigDict(from_attributes=True)



class MeasurementCreate(BaseModel):
    model_config = API_CONFIG

    cow_id: int = Field(
        alias="cowId",
        gt=0
    )

    recorded_at: datetime = Field(
        alias="recordedAt"
    )

    weight_kg: float | None = Field(
        alias="weightKg",
        gt=0,
        default=None
    )

    height_cm: float | None = Field(
        alias="heightCm",
        gt=0,
        default=None
    )

    heart_girth_cm: float | None = Field(
        alias="heartGirthCm",
        gt=0,
        default=None
    )

    body_condition_score: float | None = Field(
        alias="bodyConditionScore",
        ge=1,
        le=5,
        default=None
    )

    notes: str | None = Field(
        alias="notes",
        default=None,
        max_length=measurements_notes_length
    )

    @model_validator(mode="after")
    def one_measurement_required(self) -> Self:
        measurements = (
            self.weight_kg,
            self.height_cm,
            self.heart_girth_cm,
            self.body_condition_score,
        )
        if all(value is None for value in measurements):
            raise ValueError("At least one measurement value is required")
        return self

class MeasurementRead(MeasurementCreate):
    id: int

    model_config = ORM_CONFIG



class CowDetails(CowRead):
    measurements: list[MeasurementRead] = Field(default_factory=list)

class FarmerDetails(FarmerRead):
    cows: list[CowRead] = Field(default_factory=list)
