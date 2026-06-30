from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alcc.shared.domain.enums import VehicleState
from alcc.shared.infrastructure.database.models import TelemetryModel
from alcc.tracking.domain.entities import TelemetrySnapshot


class TelemetryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, snapshot: TelemetrySnapshot) -> TelemetrySnapshot:
        self._session.add(
            TelemetryModel(
                id=snapshot.id,
                vehicle_id=snapshot.vehicle_id,
                latitude=snapshot.latitude,
                longitude=snapshot.longitude,
                speed_kmh=snapshot.speed_kmh,
                fuel_level=snapshot.fuel_level,
                state=snapshot.state.value,
                recorded_at=snapshot.recorded_at,
            )
        )
        await self._session.flush()
        return snapshot

    async def get_latest_by_vehicle(self, vehicle_id: UUID) -> TelemetrySnapshot | None:
        result = await self._session.execute(
            select(TelemetryModel)
            .where(TelemetryModel.vehicle_id == vehicle_id)
            .order_by(TelemetryModel.recorded_at.desc())
            .limit(1)
        )
        model = result.scalar_one_or_none()
        if not model:
            return None
        return TelemetrySnapshot(
            id=model.id,
            vehicle_id=model.vehicle_id,
            latitude=model.latitude,
            longitude=model.longitude,
            speed_kmh=model.speed_kmh,
            fuel_level=model.fuel_level,
            state=VehicleState(model.state),
            recorded_at=model.recorded_at,
        )

    async def get_history(self, vehicle_id: UUID, limit: int = 100) -> list[TelemetrySnapshot]:
        result = await self._session.execute(
            select(TelemetryModel)
            .where(TelemetryModel.vehicle_id == vehicle_id)
            .order_by(TelemetryModel.recorded_at.desc())
            .limit(limit)
        )
        return [
            TelemetrySnapshot(
                id=m.id,
                vehicle_id=m.vehicle_id,
                latitude=m.latitude,
                longitude=m.longitude,
                speed_kmh=m.speed_kmh,
                fuel_level=m.fuel_level,
                state=VehicleState(m.state),
                recorded_at=m.recorded_at,
            )
            for m in result.scalars().all()
        ]
