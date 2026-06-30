from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from alcc.auth.domain.entities import User
from alcc.auth.presentation.dependencies import get_current_user, require_roles
from alcc.fleet.domain.entities import GeoPosition, Vehicle, VirtualDriver
from alcc.fleet.infrastructure.repositories import VehicleRepository, VirtualDriverRepository
from alcc.fleet.presentation.schemas import (
    AssignDriverRequest,
    DriverCreateRequest,
    DriverResponse,
    VehicleCreateRequest,
    VehicleResponse,
    VehicleStateUpdateRequest,
)
from alcc.shared.domain.enums import UserRole, VehicleState
from alcc.shared.domain.exceptions import ValidationError
from alcc.shared.infrastructure.database.session import get_db_session

router = APIRouter(prefix="/fleet", tags=["Fleet"])


def _vehicle_response(v: Vehicle) -> VehicleResponse:
    return VehicleResponse(
        id=v.id,
        license_plate=v.license_plate,
        model=v.model,
        state=v.state,
        fuel_level=v.fuel_level,
        latitude=v.position.latitude,
        longitude=v.position.longitude,
        speed_kmh=v.speed_kmh,
        driver_id=v.driver_id,
        mission_id=v.mission_id,
    )


@router.post("/vehicles", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    body: VehicleCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles(UserRole.OPERATOR, UserRole.ADMIN)),
) -> VehicleResponse:
    repo = VehicleRepository(session)
    vehicle = Vehicle(
        license_plate=body.license_plate.upper(),
        model=body.model,
        position=GeoPosition(body.latitude, body.longitude),
    )
    vehicle.register()
    await repo.save(vehicle)
    return _vehicle_response(vehicle)


@router.get("/vehicles", response_model=list[VehicleResponse])
async def list_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    state: VehicleState | None = None,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[VehicleResponse]:
    repo = VehicleRepository(session)
    if state:
        vehicles = await repo.get_by_state(state)
    else:
        vehicles = await repo.get_all(skip=skip, limit=limit)
    return [_vehicle_response(v) for v in vehicles]


@router.get("/vehicles/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> VehicleResponse:
    repo = VehicleRepository(session)
    vehicle = await repo.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return _vehicle_response(vehicle)


@router.patch("/vehicles/{vehicle_id}/state", response_model=VehicleResponse)
async def update_vehicle_state(
    vehicle_id: UUID,
    body: VehicleStateUpdateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles(UserRole.OPERATOR, UserRole.ADMIN)),
) -> VehicleResponse:
    repo = VehicleRepository(session)
    vehicle = await repo.get_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    try:
        if body.state == VehicleState.MAINTENANCE:
            vehicle.enter_maintenance()
        elif body.state == VehicleState.IDLE and vehicle.state == VehicleState.INCIDENT:
            vehicle.resolve_incident()
        else:
            raise ValidationError("Invalid state transition")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    await repo.save(vehicle)
    return _vehicle_response(vehicle)


@router.post("/vehicles/{vehicle_id}/assign-driver", response_model=VehicleResponse)
async def assign_driver(
    vehicle_id: UUID,
    body: AssignDriverRequest,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles(UserRole.DISPATCHER, UserRole.ADMIN)),
) -> VehicleResponse:
    vehicle_repo = VehicleRepository(session)
    driver_repo = VirtualDriverRepository(session)
    vehicle = await vehicle_repo.get_by_id(vehicle_id)
    driver = await driver_repo.get_by_id(body.driver_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    try:
        driver.assign_to_vehicle(vehicle_id)
        vehicle.assign_driver(body.driver_id)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    await driver_repo.save(driver)
    await vehicle_repo.save(vehicle)
    return _vehicle_response(vehicle)


@router.post("/drivers", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
async def create_driver(
    body: DriverCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles(UserRole.OPERATOR, UserRole.ADMIN)),
) -> DriverResponse:
    repo = VirtualDriverRepository(session)
    driver = VirtualDriver(name=body.name, experience_years=body.experience_years)
    await repo.save(driver)
    return DriverResponse(
        id=driver.id, name=driver.name, status=driver.status,
        vehicle_id=driver.vehicle_id, experience_years=driver.experience_years,
    )


@router.get("/drivers", response_model=list[DriverResponse])
async def list_drivers(
    available_only: bool = False,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[DriverResponse]:
    repo = VirtualDriverRepository(session)
    drivers = await repo.get_available() if available_only else await repo.get_all()
    return [
        DriverResponse(
            id=d.id, name=d.name, status=d.status,
            vehicle_id=d.vehicle_id, experience_years=d.experience_years,
        )
        for d in drivers
    ]


@router.get("/stats")
async def fleet_stats(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> dict:
    repo = VehicleRepository(session)
    total = await repo.count()
    stats = {}
    for state in VehicleState:
        count = len(await repo.get_by_state(state))
        stats[state.value] = count
    return {"total": total, "by_state": stats}
