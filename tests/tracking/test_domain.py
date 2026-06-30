from datetime import UTC, datetime, timedelta
from uuid import uuid4

from alcc.shared.domain.enums import VehicleState
from alcc.tracking.domain.entities import TelemetrySnapshot


class TestTelemetryDomain:
    def test_from_vehicle_factory(self):
        vid = uuid4()
        snapshot = TelemetrySnapshot.from_vehicle(
            vid, 48.8566, 2.3522, 60.0, 85.0, VehicleState.EN_ROUTE
        )
        assert snapshot.vehicle_id == vid
        assert snapshot.latitude == 48.8566
        assert snapshot.speed_kmh == 60.0
        assert snapshot.state == VehicleState.EN_ROUTE

    def test_to_dict(self):
        vid = uuid4()
        snapshot = TelemetrySnapshot.from_vehicle(vid, 40.0, -74.0, 50.0, 70.0, VehicleState.IDLE)
        data = snapshot.to_dict()
        assert data["vehicle_id"] == str(vid)
        assert data["state"] == "idle"
        assert "recorded_at" in data

    def test_is_stale_fresh_data(self):
        snapshot = TelemetrySnapshot(
            vehicle_id=uuid4(),
            recorded_at=datetime.now(UTC),
        )
        assert snapshot.is_stale() is False

    def test_is_stale_old_data(self):
        snapshot = TelemetrySnapshot(
            vehicle_id=uuid4(),
            recorded_at=datetime.now(UTC) - timedelta(seconds=10),
        )
        assert snapshot.is_stale(threshold_seconds=5.0) is True

    def test_default_fuel_level(self):
        snapshot = TelemetrySnapshot(vehicle_id=uuid4())
        assert snapshot.fuel_level == 100.0
