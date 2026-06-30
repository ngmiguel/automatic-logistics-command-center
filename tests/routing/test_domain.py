import pytest

from alcc.fleet.domain.entities import GeoPosition
from alcc.routing.domain.entities import Mission, RouteWaypoint
from alcc.shared.domain.enums import MissionStatus
from alcc.shared.domain.exceptions import ValidationError


class TestMissionDomain:
    def test_create_mission(self):
        mission = Mission(
            origin=GeoPosition(48.8566, 2.3522),
            destination=GeoPosition(40.7128, -74.0060),
        )
        mission.create()
        assert mission.status == MissionStatus.PENDING
        assert mission.compute_distance() > 5000

    def test_haversine_same_point(self):
        dist = Mission.haversine_km(48.8566, 2.3522, 48.8566, 2.3522)
        assert dist == 0.0

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
        assert mission.vehicle_id == vehicle_id
        mission.start()
        assert mission.status == MissionStatus.IN_PROGRESS
        assert mission.started_at is not None
        mission.complete()
        assert mission.status == MissionStatus.COMPLETED
        assert mission.completed_at is not None

    def test_cannot_complete_pending_mission(self):
        mission = Mission(origin=GeoPosition(0, 0), destination=GeoPosition(1, 1))
        with pytest.raises(ValidationError):
            mission.complete()

    def test_cannot_assign_non_pending_mission(self):
        from uuid import uuid4

        mission = Mission(origin=GeoPosition(0, 0), destination=GeoPosition(1, 1))
        mission.cancel()
        with pytest.raises(ValidationError):
            mission.assign_vehicle(uuid4())

    def test_cancel_mission(self):
        mission = Mission(origin=GeoPosition(0, 0), destination=GeoPosition(1, 1))
        mission.cancel()
        assert mission.status == MissionStatus.CANCELLED

    def test_cannot_cancel_completed_mission(self):
        mission = Mission(origin=GeoPosition(0, 0), destination=GeoPosition(1, 1))
        mission.status = MissionStatus.COMPLETED
        with pytest.raises(ValidationError):
            mission.cancel()

    def test_fail_mission(self):
        mission = Mission(origin=GeoPosition(0, 0), destination=GeoPosition(1, 1))
        mission.fail("Route blocked")
        assert mission.status == MissionStatus.FAILED

    def test_mission_completed_emits_event(self):
        mission = Mission(origin=GeoPosition(0, 0), destination=GeoPosition(1, 1))
        mission.create()
        from uuid import uuid4

        mission.assign_vehicle(uuid4())
        mission.start()
        mission.complete()
        events = mission.pull_events()
        assert any(e.event_type == "mission.completed" for e in events)

    def test_route_waypoint(self):
        wp = RouteWaypoint(latitude=48.0, longitude=2.0, sequence=1)
        assert wp.latitude == 48.0
        assert wp.sequence == 1
