from uuid import UUID

from pydantic import BaseModel

from alcc.shared.domain.enums import VehicleState


class TelemetryResponse(BaseModel):
    vehicle_id: UUID
    latitude: float
    longitude: float
    speed_kmh: float
    fuel_level: float
    state: VehicleState
    recorded_at: str
