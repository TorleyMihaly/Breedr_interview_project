

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError

from app.schemas import FarmerCreate, FarmerDetails, FarmerRead
from app.models import FarmerModel
from app.db import get_db


router = APIRouter()
SessionDep = Annotated[Session, Depends(get_db)]

@router.post("", response_model=FarmerRead, status_code=status.HTTP_201_CREATED)
def create_farmer(payload: FarmerCreate, db: SessionDep) -> FarmerModel:
    farmer = FarmerModel(
        name=payload.name,
        email=payload.email,
    )
    db.add(farmer)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Farmer email already exists",
        ) from exc
    
    db.refresh(farmer)
    return farmer

@router.get("", response_model=list[FarmerRead])
def list_farmers(db: SessionDep, limit: int = 50, offset: int = 0) -> list[FarmerModel]:
    statement = select(FarmerModel).order_by(FarmerModel.id).offset(offset).limit(limit)
    return list(db.scalars(statement))

@router.get("/{farmer_id}", response_model=FarmerDetails)
def get_farmer(farmer_id: int, db: SessionDep) -> FarmerModel:
    statement = (select(FarmerModel).options(selectinload(FarmerModel.cows)).where(FarmerModel.id == farmer_id))
    farmer = db.scalar(statement)

    if farmer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found",
        )

    return farmer

@router.delete("/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farmer(farmer_id: int, db: SessionDep) -> None:
    farmer = db.get(FarmerModel, farmer_id)

    if farmer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found",
        )

    db.delete(farmer)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Farmer could not be deleted",
        ) from exc
