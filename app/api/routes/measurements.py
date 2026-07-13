from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import CowMeasurementModel, CowModel, FarmerModel
from app.schemas import CowCreate, CowDetails, CowRead, FarmerCreate, MeasurementCreate, MeasurementRead
from app.db import get_db


router = APIRouter()
SessionDep = Annotated[Session, Depends(get_db)]



@router.post("", response_model=MeasurementRead, status_code=status.HTTP_201_CREATED)
def create_measurement(payload: MeasurementCreate, db: SessionDep) -> CowMeasurementModel:
    cow = db.get(CowModel, payload.cow_id)
    if cow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cow not found",
        )
    
    measurement = CowMeasurementModel(**payload.model_dump(exclude_none=True))
    db.add(measurement)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create measurement",
        ) from exc
    
    db.refresh(measurement)
    return measurement


@router.get("", response_model=list[MeasurementRead])
def get_measurements(cow_id: Annotated[int, Query(alias="cowId", gt=0)], db: SessionDep) -> list[CowMeasurementModel]:
    cow = db.get(CowModel, cow_id)
    if cow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cow not found",
        )
    
    statement = select(CowMeasurementModel).where(CowMeasurementModel.cow_id == cow_id).order_by(CowMeasurementModel.recorded_at.desc())

    return list(db.scalars(statement))

@router.delete("/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_measurement(measurement_id: int, db: SessionDep) -> None:
    measurement = db.get(CowMeasurementModel, measurement_id)

    if measurement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurement not found",
        )

    db.delete(measurement)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Measurement could not be deleted",
        ) from exc
