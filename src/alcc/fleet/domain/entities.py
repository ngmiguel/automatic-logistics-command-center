from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from alcc.shared.domain.base import AggregateRoot, DomainEvent, ValueObject
from alcc.shared.domain.enums import DriverStatus, VehicleState
from alcc.shared.domain.exceptions import ValidationError


@dataclass(frozen=True)
class GeoPosition(ValueObject):
    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        if not -90 <= self.latitude <= 90:
            raise ValidationError("Latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValidationError("Longitude must be between -180 and 180")


@dataclass
class VehicleRegistered(DomainEvent):
    event_type: str = "vehicle.registered"


@dataclass
class VehicleStateChanged(DomainEvent):
    event_type: str = "vehicle.state_changed"
    old_state: VehicleState = VehicleState.IDLE
    new_state: VehicleState = VehicleState.IDLE


@dataclass
class Vehicle(AggregateRoot):
    license_plate: str = ""
    model: str = ""
    state: VehicleState = VehicleState.IDLE
    fuel_level: float = 100.0
    position: GeoPosition = field(default_factory=lambda: GeoPosition(0.0, 0.0))
    speed_kmh: float = 0.0
    driver_id: UUID | None = None
    mission_id: UUID | None = None
    max_fuel: float = 100.0

    def register(self) -> None:
        self._register_event(VehicleRegistered(aggregate_id=self.id))

    def assign_driver(self, driver_id: UUID) -> None:
        if self.state in (VehicleState.MAINTENANCE, VehicleState.INCIDENT):
            raise ValidationError(f"Cannot assign driver while vehicle is {self.state}")
        self.driver_id = driver_id
        self.updated_at = datetime.now(UTC)

    def assign_mission(self, mission_id: UUID) -> None:
        if self.state != VehicleState.IDLE:
            raise ValidationError("Only idle vehicles can receive missions")
        if self.driver_id is None:
            raise ValidationError("Vehicle must have an assigned driver")
        self.mission_id = mission_id
        self._change_state(VehicleState.EN_ROUTE)

    def complete_mission(self) -> None:
        if self.state != VehicleState.EN_ROUTE:
            raise ValidationError("Vehicle is not en route")
        self.mission_id = None
        self.speed_kmh = 0.0
        self._change_state(VehicleState.IDLE)

    def enter_maintenance(self) -> None:
        if self.state == VehicleState.EN_ROUTE:
            raise ValidationError("Cannot enter maintenance while en route")
        self.mission_id = None
        self.speed_kmh = 0.0
        self._change_state(VehicleState.MAINTENANCE)

    def resolve_incident(self) -> None:
        if self.state != VehicleState.INCIDENT:
            raise ValidationError("Vehicle is not in incident state")
        self._change_state(VehicleState.IDLE)

    def trigger_incident(self) -> None:
        self.speed_kmh = 0.0
        self._change_state(VehicleState.INCIDENT)

    def consume_fuel(self, amount: float) -> None:
        self.fuel_level = max(0.0, self.fuel_level - amount)
        if self.fuel_level <= 0 and self.state == VehicleState.EN_ROUTE:
            self.trigger_incident()

    def refuel(self, amount: float) -> None:
        self.fuel_level = min(self.max_fuel, self.fuel_level + amount)
        self.updated_at = datetime.now(UTC)

    def update_telemetry(self, latitude: float, longitude: float, speed_kmh: float) -> None:
        self.position = GeoPosition(latitude, longitude)
        self.speed_kmh = speed_kmh
        self.updated_at = datetime.now(UTC)

    def _change_state(self, new_state: VehicleState) -> None:
        old_state = self.state
        self.state = new_state
        self.updated_at = datetime.now(UTC)
        self._register_event(
            VehicleStateChanged(
                aggregate_id=self.id,
                old_state=old_state,
                new_state=new_state,
            )
        )


@dataclass
class VirtualDriver(AggregateRoot):
    name: str = ""
    status: DriverStatus = DriverStatus.AVAILABLE
    vehicle_id: UUID | None = None
    experience_years: int = 0

    def assign_to_vehicle(self, vehicle_id: UUID) -> None:
        if self.status != DriverStatus.AVAILABLE:
            raise ValidationError("Driver is not available")
        self.vehicle_id = vehicle_id
        self.status = DriverStatus.ASSIGNED
        self.updated_at = datetime.now(UTC)

    def release(self) -> None:
        self.vehicle_id = None
        self.status = DriverStatus.AVAILABLE
        self.updated_at = datetime.now(UTC)
