from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    OPERATOR = "operator"
    DISPATCHER = "dispatcher"
    ANALYST = "analyst"


class VehicleState(StrEnum):
    IDLE = "idle"
    EN_ROUTE = "en_route"
    MAINTENANCE = "maintenance"
    INCIDENT = "incident"
    OFFLINE = "offline"


class MissionStatus(StrEnum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class IncidentSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class NotificationType(StrEnum):
    INCIDENT = "incident"
    LOW_FUEL = "low_fuel"
    MISSION_DELAY = "mission_delay"
    MAINTENANCE = "maintenance"
    SYSTEM = "system"


class DriverStatus(StrEnum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    OFF_DUTY = "off_duty"
