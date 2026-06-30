from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from alcc.shared.domain.base import AggregateRoot, DomainEvent
from alcc.shared.domain.enums import IncidentSeverity, NotificationType


@dataclass
class NotificationSent(DomainEvent):
    event_type: str = "notification.sent"


@dataclass
class Notification(AggregateRoot):
    type: NotificationType = NotificationType.SYSTEM
    title: str = ""
    message: str = ""
    severity: IncidentSeverity = IncidentSeverity.LOW
    vehicle_id: UUID | None = None
    mission_id: UUID | None = None
    is_read: bool = False
    read_at: datetime | None = None

    def mark_read(self) -> None:
        self.is_read = True
        self.read_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def publish(self) -> None:
        self._register_event(NotificationSent(aggregate_id=self.id))


@dataclass
class Incident(AggregateRoot):
    vehicle_id: UUID = field(default_factory=lambda: UUID(int=0))
    severity: IncidentSeverity = IncidentSeverity.LOW
    description: str = ""
    resolved: bool = False
    resolved_at: datetime | None = None

    def resolve(self) -> None:
        self.resolved = True
        self.resolved_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)
