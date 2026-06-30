from uuid import UUID

from pydantic import BaseModel, Field

from alcc.shared.domain.enums import DriverStatus, VehicleState


class VehicleCreateRequest(BaseModel):
    license_plate: str = Field(min_length=3, max_length=20)
    model: str = Field(default="Autonomous Truck v2")
    latitude: float = Field(default=48.8566, ge=-90, le=90)
    longitude: float = Field(default=2.3522, ge=-180, le=180)


class VehicleResponse(BaseModel):
    id: UUID
    license_plate: str
    model: str
    state: VehicleState
    fuel_level: float
    latitude: float
    longitude: float
    speed_kmh: float
    driver_id: UUID | None
    mission_id: UUID | None


class VehicleStateUpdateRequest(BaseModel):
    state: VehicleState


class DriverCreateRequest(BaseModel):
    name: str = Field(min_length=2)
    experience_years: int = Field(default=1, ge=0)


class DriverResponse(BaseModel):
    id: UUID
    name: str
    status: DriverStatus
    vehicle_id: UUID | None
    experience_years: int


class AssignDriverRequest(BaseModel):
    driver_id: UUID
