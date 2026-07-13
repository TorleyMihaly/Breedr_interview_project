from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import CowMeasurementModel, CowModel, FarmerModel
from app.schemas import CowCreate, CowDetails, CowRead, FarmerCreate, MeasurementCreate, MeasurementRead
from app.db import get_db


router = APIRouter()
SessionDep = Annotated[Session, Depends(get_db)]

@router.post("", response_model=CowRead, status_code=status.HTTP_201_CREATED)
def create_cow(payload: CowCreate, db: SessionDep) -> CowModel:
    farmer = db.get(FarmerModel, payload.farmer_id)
    if farmer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found",
        )
    
    cow = CowModel(
        tag_number=payload.tag_number,
        name=payload.name,
        breed=payload.breed,
        date_of_birth=payload.date_of_birth,
        farmer_id=payload.farmer_id,
    )
    db.add(cow)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cow already exists for this farmer",
        ) from exc
    
    db.refresh(cow)
    return cow

@router.get("", response_model=list[CowRead])
def list_cows(db: SessionDep, farmer_id: int | None = None, limit: int = 50, offset: int = 0) -> list[CowModel]:
    statement = select(CowModel).order_by(CowModel.id)

    if farmer_id is not None:
        statement = statement.where(CowModel.farmer_id == farmer_id)

    statement = statement.offset(offset).limit(limit)

    return list(db.scalars(statement))

@router.get("/{cow_id}", response_model=CowDetails)
def get_cow(cow_id: int, db: SessionDep) -> CowModel:
    statement = (select(CowModel).options(selectinload(CowModel.measurements)).where(CowModel.id == cow_id))
    cow = db.scalar(statement)

    if cow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cow not found",
        )

    return cow

@router.delete("/{cow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cow(cow_id: int, db: SessionDep) -> None:
    cow = db.get(CowModel, cow_id)

    if cow is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cow not found",
        )

    db.delete(cow)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cow could not be deleted",
        ) from exc
