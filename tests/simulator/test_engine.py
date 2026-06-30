from uuid import uuid4

import pytest

from alcc.fleet.domain.entities import GeoPosition, Vehicle
from alcc.fleet.infrastructure.repositories import VehicleRepository
from alcc.routing.domain.entities import Mission
from alcc.routing.infrastructure.repositories import MissionRepository
from alcc.shared.domain.enums import MissionStatus, VehicleState
from alcc.simulator.engine import WORLD_CITIES, VehicleSimulator


class TestSimulatorEngine:
    def test_world_cities_defined(self):
        assert len(WORLD_CITIES) >= 10
        for lat, lng in WORLD_CITIES:
            assert -90 <= lat <= 90
            assert -180 <= lng <= 180

    @pytest.mark.asyncio
    async def test_seed_fleet(self, db_session):
        sim = VehicleSimulator()
        count = await sim.seed_fleet(count=5)
        assert count == 5

    @pytest.mark.asyncio
    async def test_seed_fleet_idempotent(self, db_session):
        sim = VehicleSimulator()
        await sim.seed_fleet(count=3)
        count = await sim.seed_fleet(count=3)
        assert count == 3

    @pytest.mark.asyncio
    async def test_move_vehicle_toward_destination(self, db_session):
        sim = VehicleSimulator()
        vehicle = Vehicle(
            license_plate="SIM-001",
            position=GeoPosition(48.0, 2.0),
            state=VehicleState.EN_ROUTE,
        )
        vehicle.driver_id = uuid4()
        mission = Mission(
            origin=GeoPosition(48.0, 2.0),
            destination=GeoPosition(49.0, 3.0),
        )
        vehicle.mission_id = mission.id
        mission.vehicle_id = vehicle.id
        mission.status = MissionStatus.IN_PROGRESS

        v_repo = VehicleRepository(db_session)
        m_repo = MissionRepository(db_session)
        await v_repo.save(vehicle)
        await m_repo.save(mission)

        initial_lat = vehicle.position.latitude
        await sim._move_vehicle(vehicle, m_repo)
        assert vehicle.position.latitude != initial_lat or vehicle.state == VehicleState.IDLE

    def test_simulator_not_running_by_default(self):
        sim = VehicleSimulator()
        assert sim._running is False
