from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from alcc.fleet.domain.entities import GeoPosition
from alcc.shared.domain.base import AggregateRoot, DomainEvent, ValueObject
from alcc.shared.domain.enums import MissionStatus
from alcc.shared.domain.exceptions import ValidationError


@dataclass
class MissionCreated(DomainEvent):
    event_type: str = "mission.created"


@dataclass
class MissionCompleted(DomainEvent):
    event_type: str = "mission.completed"


@dataclass(frozen=True)
class RouteWaypoint(ValueObject):
    latitude: float
    longitude: float
    sequence: int


@dataclass
class Mission(AggregateRoot):
    origin: GeoPosition = field(default_factory=lambda: GeoPosition(0.0, 0.0))
    destination: GeoPosition = field(default_factory=lambda: GeoPosition(0.0, 0.0))
    status: MissionStatus = MissionStatus.PENDING
    vehicle_id: UUID | None = None
    priority: int = 1
    cargo_description: str = ""
    estimated_distance_km: float = 0.0
    waypoints: list = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    def create(self) -> None:
        self._register_event(MissionCreated(aggregate_id=self.id))

    def assign_vehicle(self, vehicle_id: UUID) -> None:
        if self.status != MissionStatus.PENDING:
            raise ValidationError("Only pending missions can be assigned")
        self.vehicle_id = vehicle_id
        self.status = MissionStatus.ASSIGNED
        self.updated_at = datetime.now(UTC)

    def start(self) -> None:
        if self.status != MissionStatus.ASSIGNED:
            raise ValidationError("Mission must be assigned before starting")
        self.status = MissionStatus.IN_PROGRESS
        self.started_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def complete(self) -> None:
        if self.status != MissionStatus.IN_PROGRESS:
            raise ValidationError("Only in-progress missions can be completed")
        self.status = MissionStatus.COMPLETED
        self.completed_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
        self._register_event(MissionCompleted(aggregate_id=self.id))

    def cancel(self) -> None:
        if self.status in (MissionStatus.COMPLETED, MissionStatus.CANCELLED):
            raise ValidationError("Mission cannot be cancelled")
        self.status = MissionStatus.CANCELLED
        self.updated_at = datetime.now(UTC)

    def fail(self, reason: str = "") -> None:
        self.status = MissionStatus.FAILED
        self.updated_at = datetime.now(UTC)

    @staticmethod
    def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        import math

        r = 6371.0
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )
        return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def compute_distance(self) -> float:
        return self.haversine_km(
            self.origin.latitude,
            self.origin.longitude,
            self.destination.latitude,
            self.destination.longitude,
        )
