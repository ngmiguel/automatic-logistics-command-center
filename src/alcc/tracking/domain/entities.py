from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from alcc.shared.domain.base import DomainEvent, Entity
from alcc.shared.domain.enums import VehicleState


@dataclass
class TelemetryReceived(DomainEvent):
    event_type: str = "telemetry.received"


@dataclass
class TelemetrySnapshot(Entity):
    vehicle_id: UUID = field(default_factory=lambda: UUID(int=0))
    latitude: float = 0.0
    longitude: float = 0.0
    speed_kmh: float = 0.0
    fuel_level: float = 100.0
    state: VehicleState = VehicleState.IDLE
    recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def from_vehicle(
        cls,
        vehicle_id: UUID,
        latitude: float,
        longitude: float,
        speed_kmh: float,
        fuel_level: float,
        state: VehicleState,
    ) -> "TelemetrySnapshot":
        return cls(
            vehicle_id=vehicle_id,
            latitude=latitude,
            longitude=longitude,
            speed_kmh=speed_kmh,
            fuel_level=fuel_level,
            state=state,
            recorded_at=datetime.now(UTC),
        )

    def is_stale(self, threshold_seconds: float = 5.0) -> bool:
        age = (datetime.now(UTC) - self.recorded_at).total_seconds()
        return age > threshold_seconds

    def to_dict(self) -> dict:
        return {
            "vehicle_id": str(self.vehicle_id),
            "latitude": self.latitude,
            "longitude": self.longitude,
            "speed_kmh": self.speed_kmh,
            "fuel_level": self.fuel_level,
            "state": self.state.value,
            "recorded_at": self.recorded_at.isoformat(),
        }
