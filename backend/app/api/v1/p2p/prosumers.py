from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.schemas.p2p.prosumer import (
    ProsumerCreate, ProsumerRead, ProsumerUpdate,
    MeterReadingCreate, MeterReadingRead,
)
from app.services.p2p.prosumer_service import ProsumerService

router = APIRouter()


@router.post(
    "/",
    response_model=ProsumerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register as a prosumer",
)
async def register_prosumer(
    payload: ProsumerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = await ProsumerService.get_by_user_id(db, current_user.id)
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Already registered as prosumer")
    return await ProsumerService.register(db, current_user.id, payload)


@router.get(
    "/me",
    response_model=ProsumerRead,
    summary="Get own prosumer profile",
)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    return profile


@router.patch(
    "/me",
    response_model=ProsumerRead,
    summary="Update prosumer profile",
)
async def update_my_profile(
    payload: ProsumerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    updated = await ProsumerService.update(db, profile.id, payload)
    return updated


@router.post(
    "/meter-readings",
    summary="Ingest smart meter readings",
    status_code=status.HTTP_201_CREATED,
)
async def ingest_meter_readings(
    readings: list[MeterReadingCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = await ProsumerService.ingest_meter_readings(db, current_user.id, readings)
    if count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    return {"inserted": count}


@router.get(
    "/meter-readings",
    response_model=list[MeterReadingRead],
    summary="Query meter readings",
)
async def get_meter_readings(
    start: datetime = Query(...),
    end: datetime = Query(...),
    limit: int = Query(200, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await ProsumerService.get_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not registered as prosumer")
    return await ProsumerService.get_meter_readings(db, profile.id, start, end, limit)
