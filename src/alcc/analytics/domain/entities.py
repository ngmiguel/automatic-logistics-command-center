from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class FleetKPIs:
    total_vehicles: int = 0
    active_vehicles: int = 0
    idle_vehicles: int = 0
    en_route_vehicles: int = 0
    maintenance_vehicles: int = 0
    incident_vehicles: int = 0
    offline_vehicles: int = 0
    fleet_utilization_rate: float = 0.0
    average_fuel_level: float = 0.0
    average_speed_kmh: float = 0.0
    computed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        return {
            "total_vehicles": self.total_vehicles,
            "active_vehicles": self.active_vehicles,
            "idle_vehicles": self.idle_vehicles,
            "en_route_vehicles": self.en_route_vehicles,
            "maintenance_vehicles": self.maintenance_vehicles,
            "incident_vehicles": self.incident_vehicles,
            "offline_vehicles": self.offline_vehicles,
            "fleet_utilization_rate": round(self.fleet_utilization_rate, 4),
            "average_fuel_level": round(self.average_fuel_level, 2),
            "average_speed_kmh": round(self.average_speed_kmh, 2),
            "computed_at": self.computed_at.isoformat(),
        }


@dataclass
class MissionKPIs:
    total_missions: int = 0
    pending: int = 0
    in_progress: int = 0
    completed: int = 0
    cancelled: int = 0
    failed: int = 0
    completion_rate: float = 0.0
    computed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        return {
            "total_missions": self.total_missions,
            "pending": self.pending,
            "in_progress": self.in_progress,
            "completed": self.completed,
            "cancelled": self.cancelled,
            "failed": self.failed,
            "completion_rate": round(self.completion_rate, 4),
            "computed_at": self.computed_at.isoformat(),
        }


@dataclass
class IncidentKPIs:
    total_incidents: int = 0
    open_incidents: int = 0
    resolved_incidents: int = 0
    critical_incidents: int = 0
    incident_rate: float = 0.0
    computed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        return {
            "total_incidents": self.total_incidents,
            "open_incidents": self.open_incidents,
            "resolved_incidents": self.resolved_incidents,
            "critical_incidents": self.critical_incidents,
            "incident_rate": round(self.incident_rate, 4),
            "computed_at": self.computed_at.isoformat(),
        }
