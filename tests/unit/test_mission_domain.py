import pytest

from alcc.fleet.domain.entities import GeoPosition
from alcc.routing.domain.entities import Mission
from alcc.shared.domain.enums import MissionStatus
from alcc.shared.domain.exceptions import ValidationError


class TestMission:
    def test_create_mission(self):
        mission = Mission(
            origin=GeoPosition(48.8566, 2.3522),
            destination=GeoPosition(40.7128, -74.0060),
        )
        mission.create()
        assert mission.status == MissionStatus.PENDING
        assert mission.compute_distance() > 5000

    def test_mission_lifecycle(self):
        from uuid import uuid4

        mission = Mission(
            origin=GeoPosition(48.8566, 2.3522),
            destination=GeoPosition(51.5074, -0.1278),
        )
        mission.create()
        vehicle_id = uuid4()
        mission.assign_vehicle(vehicle_id)
        assert mission.status == MissionStatus.ASSIGNED
        mission.start()
        assert mission.status == MissionStatus.IN_PROGRESS
        mission.complete()
        assert mission.status == MissionStatus.COMPLETED

    def test_cannot_complete_pending_mission(self):
        mission = Mission(
            origin=GeoPosition(0, 0),
            destination=GeoPosition(1, 1),
        )
        with pytest.raises(ValidationError):
            mission.complete()

    def test_cancel_mission(self):
        mission = Mission(
            origin=GeoPosition(0, 0),
            destination=GeoPosition(1, 1),
        )
        mission.cancel()
        assert mission.status == MissionStatus.CANCELLED
