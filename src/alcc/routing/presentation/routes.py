from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from alcc.auth.domain.entities import User
from alcc.auth.presentation.dependencies import get_current_user, require_roles
from alcc.fleet.infrastructure.repositories import VehicleRepository
from alcc.routing.domain.entities import GeoPosition, Mission
from alcc.routing.infrastructure.repositories import MissionRepository
from alcc.routing.presentation.schemas import (
    AssignMissionRequest,
    MissionCreateRequest,
    MissionResponse,
)
from alcc.shared.domain.enums import MissionStatus, UserRole, VehicleState
from alcc.shared.domain.exceptions import ValidationError
from alcc.shared.infrastructure.database.session import get_db_session

router = APIRouter(prefix="/missions", tags=["Routing"])


def _mission_response(m: Mission) -> MissionResponse:
    return MissionResponse(
        id=m.id,
        origin_lat=m.origin.latitude,
        origin_lng=m.origin.longitude,
        dest_lat=m.destination.latitude,
        dest_lng=m.destination.longitude,
        status=m.status,
        vehicle_id=m.vehicle_id,
        priority=m.priority,
        cargo_description=m.cargo_description,
        estimated_distance_km=m.estimated_distance_km,
    )


@router.post("", response_model=MissionResponse, status_code=status.HTTP_201_CREATED)
async def create_mission(
    body: MissionCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles(UserRole.DISPATCHER, UserRole.ADMIN)),
) -> MissionResponse:
    mission = Mission(
        origin=GeoPosition(body.origin_lat, body.origin_lng),
        destination=GeoPosition(body.dest_lat, body.dest_lng),
        priority=body.priority,
        cargo_description=body.cargo_description,
    )
    mission.estimated_distance_km = mission.compute_distance()
    mission.create()
    repo = MissionRepository(session)
    await repo.save(mission)
    return _mission_response(mission)


@router.get("", response_model=list[MissionResponse])
async def list_missions(
    status_filter: MissionStatus | None = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[MissionResponse]:
    repo = MissionRepository(session)
    if status_filter:
        missions = await repo.get_by_status(status_filter)
    else:
        missions = await repo.get_all(skip=skip, limit=limit)
    return [_mission_response(m) for m in missions]


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission(
    mission_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> MissionResponse:
    repo = MissionRepository(session)
    mission = await repo.get_by_id(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return _mission_response(mission)


@router.post("/{mission_id}/assign", response_model=MissionResponse)
async def assign_mission(
    mission_id: UUID,
    body: AssignMissionRequest,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles(UserRole.DISPATCHER, UserRole.ADMIN)),
) -> MissionResponse:
    mission_repo = MissionRepository(session)
    vehicle_repo = VehicleRepository(session)
    mission = await mission_repo.get_by_id(mission_id)
    vehicle = await vehicle_repo.get_by_id(body.vehicle_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.state != VehicleState.IDLE:
        raise HTTPException(status_code=400, detail="Vehicle is not idle")
    try:
        mission.assign_vehicle(body.vehicle_id)
        mission.start()
        vehicle.assign_mission(mission_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    await mission_repo.save(mission)
    await vehicle_repo.save(vehicle)
    return _mission_response(mission)


@router.post("/{mission_id}/complete", response_model=MissionResponse)
async def complete_mission(
    mission_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles(UserRole.DISPATCHER, UserRole.OPERATOR, UserRole.ADMIN)),
) -> MissionResponse:
    mission_repo = MissionRepository(session)
    vehicle_repo = VehicleRepository(session)
    mission = await mission_repo.get_by_id(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    try:
        mission.complete()
        if mission.vehicle_id:
            vehicle = await vehicle_repo.get_by_id(mission.vehicle_id)
            if vehicle:
                vehicle.complete_mission()
                await vehicle_repo.save(vehicle)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    await mission_repo.save(mission)
    return _mission_response(mission)


@router.post("/{mission_id}/cancel", response_model=MissionResponse)
async def cancel_mission(
    mission_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles(UserRole.DISPATCHER, UserRole.ADMIN)),
) -> MissionResponse:
    repo = MissionRepository(session)
    mission = await repo.get_by_id(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    try:
        mission.cancel()
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    await repo.save(mission)
    return _mission_response(mission)
