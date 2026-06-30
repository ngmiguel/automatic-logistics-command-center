from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from alcc.auth.domain.entities import User
from alcc.auth.presentation.dependencies import get_current_user
from alcc.shared.infrastructure.database.session import get_db_session
from alcc.shared.infrastructure.redis_client import redis_client
from alcc.tracking.infrastructure.repositories import TelemetryRepository
from alcc.tracking.presentation.schemas import TelemetryResponse

router = APIRouter(prefix="/tracking", tags=["Tracking"])


@router.get("/vehicles/{vehicle_id}/latest", response_model=TelemetryResponse)
async def get_latest_telemetry(
    vehicle_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> TelemetryResponse:
    cached = await redis_client.get_telemetry(str(vehicle_id))
    if cached:
        return TelemetryResponse(**cached)
    repo = TelemetryRepository(session)
    snapshot = await repo.get_latest_by_vehicle(vehicle_id)
    if not snapshot:
        raise HTTPException(status_code=404, detail="No telemetry found")
    return TelemetryResponse(**snapshot.to_dict())


@router.get("/vehicles/{vehicle_id}/history", response_model=list[TelemetryResponse])
async def get_telemetry_history(
    vehicle_id: UUID,
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[TelemetryResponse]:
    repo = TelemetryRepository(session)
    history = await repo.get_history(vehicle_id, limit=limit)
    return [TelemetryResponse(**s.to_dict()) for s in history]


@router.get("/live", response_model=list[TelemetryResponse])
async def get_live_fleet_telemetry(
    _: User = Depends(get_current_user),
) -> list[TelemetryResponse]:
    vehicle_ids = await redis_client.get_all_telemetry_keys()
    results = []
    for vid in vehicle_ids[:1000]:
        data = await redis_client.get_telemetry(vid)
        if data:
            results.append(TelemetryResponse(**data))
    return results
