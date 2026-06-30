from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from alcc.shared.domain.enums import VehicleState
from alcc.tracking.domain.entities import TelemetrySnapshot
from alcc.tracking.infrastructure.repositories import TelemetryRepository


@pytest.mark.asyncio
class TestTrackingRepository:
    async def test_save_and_get_latest(self, db_session: AsyncSession):
        repo = TelemetryRepository(db_session)
        vid = uuid4()
        snapshot = TelemetrySnapshot.from_vehicle(
            vid, 48.0, 2.0, 55.0, 80.0, VehicleState.EN_ROUTE
        )
        await repo.save(snapshot)
        latest = await repo.get_latest_by_vehicle(vid)
        assert latest is not None
        assert latest.latitude == 48.0

    async def test_get_history(self, db_session: AsyncSession):
        repo = TelemetryRepository(db_session)
        vid = uuid4()
        for i in range(3):
            await repo.save(
                TelemetrySnapshot.from_vehicle(
                    vid, 48.0 + i, 2.0, 50.0, 80.0, VehicleState.EN_ROUTE
                )
            )
        history = await repo.get_history(vid, limit=2)
        assert len(history) == 2


@pytest.mark.asyncio
class TestTrackingAPI:
    async def test_get_latest_from_db(
        self, client: AsyncClient, operator_headers: dict, db_session: AsyncSession
    ):
        vid = uuid4()
        repo = TelemetryRepository(db_session)
        await repo.save(
            TelemetrySnapshot.from_vehicle(vid, 48.0, 2.0, 50.0, 90.0, VehicleState.IDLE)
        )
        await db_session.commit()
        response = await client.get(
            f"/api/v1/tracking/vehicles/{vid}/latest",
            headers=operator_headers,
        )
        assert response.status_code == 200
        assert response.json()["latitude"] == 48.0

    async def test_get_latest_not_found(self, client: AsyncClient, operator_headers: dict):
        response = await client.get(
            f"/api/v1/tracking/vehicles/{uuid4()}/latest",
            headers=operator_headers,
        )
        assert response.status_code == 404

    async def test_get_live_telemetry(self, client: AsyncClient, operator_headers: dict, mock_redis):
        import json

        vid = str(uuid4())
        mock_redis[vid] = json.dumps(
            {
                "vehicle_id": vid,
                "latitude": 48.0,
                "longitude": 2.0,
                "speed_kmh": 60.0,
                "fuel_level": 75.0,
                "state": "en_route",
                "recorded_at": "2026-01-01T00:00:00+00:00",
            }
        )
        response = await client.get("/api/v1/tracking/live", headers=operator_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    async def test_get_history(
        self, client: AsyncClient, operator_headers: dict, db_session: AsyncSession
    ):
        vid = uuid4()
        repo = TelemetryRepository(db_session)
        await repo.save(
            TelemetrySnapshot.from_vehicle(vid, 48.0, 2.0, 50.0, 90.0, VehicleState.IDLE)
        )
        await db_session.commit()
        response = await client.get(
            f"/api/v1/tracking/vehicles/{vid}/history",
            headers=operator_headers,
        )
        assert response.status_code == 200
        assert len(response.json()) >= 1
