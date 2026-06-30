from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alcc.fleet.domain.entities import GeoPosition
from alcc.routing.domain.entities import Mission
from alcc.shared.domain.enums import MissionStatus
from alcc.shared.infrastructure.database.models import MissionModel


def _mission_to_domain(model: MissionModel) -> Mission:
    return Mission(
        id=model.id,
        origin=GeoPosition(model.origin_lat, model.origin_lng),
        destination=GeoPosition(model.dest_lat, model.dest_lng),
        status=MissionStatus(model.status),
        vehicle_id=model.vehicle_id,
        priority=model.priority,
        cargo_description=model.cargo_description,
        estimated_distance_km=model.estimated_distance_km,
        started_at=model.started_at,
        completed_at=model.completed_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class MissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, mission_id: UUID) -> Mission | None:
        result = await self._session.execute(
            select(MissionModel).where(MissionModel.id == mission_id)
        )
        model = result.scalar_one_or_none()
        return _mission_to_domain(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Mission]:
        result = await self._session.execute(
            select(MissionModel).offset(skip).limit(limit).order_by(MissionModel.created_at.desc())
        )
        return [_mission_to_domain(m) for m in result.scalars().all()]

    async def get_by_status(self, status: MissionStatus) -> list[Mission]:
        result = await self._session.execute(
            select(MissionModel).where(MissionModel.status == status.value)
        )
        return [_mission_to_domain(m) for m in result.scalars().all()]

    async def save(self, mission: Mission) -> Mission:
        existing = await self._session.get(MissionModel, mission.id)
        if existing:
            existing.origin_lat = mission.origin.latitude
            existing.origin_lng = mission.origin.longitude
            existing.dest_lat = mission.destination.latitude
            existing.dest_lng = mission.destination.longitude
            existing.status = mission.status.value
            existing.vehicle_id = mission.vehicle_id
            existing.priority = mission.priority
            existing.cargo_description = mission.cargo_description
            existing.estimated_distance_km = mission.estimated_distance_km
            existing.started_at = mission.started_at
            existing.completed_at = mission.completed_at
            existing.updated_at = mission.updated_at
        else:
            self._session.add(
                MissionModel(
                    id=mission.id,
                    origin_lat=mission.origin.latitude,
                    origin_lng=mission.origin.longitude,
                    dest_lat=mission.destination.latitude,
                    dest_lng=mission.destination.longitude,
                    status=mission.status.value,
                    vehicle_id=mission.vehicle_id,
                    priority=mission.priority,
                    cargo_description=mission.cargo_description,
                    estimated_distance_km=mission.estimated_distance_km,
                    started_at=mission.started_at,
                    completed_at=mission.completed_at,
                    created_at=mission.created_at,
                    updated_at=mission.updated_at,
                )
            )
        await self._session.flush()
        return mission
