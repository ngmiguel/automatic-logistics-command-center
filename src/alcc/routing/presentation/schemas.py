from uuid import UUID

from pydantic import BaseModel, Field

from alcc.shared.domain.enums import MissionStatus


class MissionCreateRequest(BaseModel):
    origin_lat: float = Field(ge=-90, le=90)
    origin_lng: float = Field(ge=-180, le=180)
    dest_lat: float = Field(ge=-90, le=90)
    dest_lng: float = Field(ge=-180, le=180)
    priority: int = Field(default=1, ge=1, le=5)
    cargo_description: str = ""


class MissionResponse(BaseModel):
    id: UUID
    origin_lat: float
    origin_lng: float
    dest_lat: float
    dest_lng: float
    status: MissionStatus
    vehicle_id: UUID | None
    priority: int
    cargo_description: str
    estimated_distance_km: float


class AssignMissionRequest(BaseModel):
    vehicle_id: UUID
