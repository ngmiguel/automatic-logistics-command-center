from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from alcc.fleet.domain.entities import GeoPosition, Vehicle, VirtualDriver
from alcc.shared.domain.enums import DriverStatus, VehicleState
from alcc.shared.infrastructure.database.models import VehicleModel, VirtualDriverModel


def _vehicle_to_domain(model: VehicleModel) -> Vehicle:
    return Vehicle(
        id=model.id,
        license_plate=model.license_plate,
        model=model.model,
        state=VehicleState(model.state),
        fuel_level=model.fuel_level,
        position=GeoPosition(model.latitude, model.longitude),
        speed_kmh=model.speed_kmh,
        driver_id=model.driver_id,
        mission_id=model.mission_id,
        max_fuel=model.max_fuel,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _vehicle_to_model(vehicle: Vehicle) -> VehicleModel:
    return VehicleModel(
        id=vehicle.id,
        license_plate=vehicle.license_plate,
        model=vehicle.model,
        state=vehicle.state.value,
        fuel_level=vehicle.fuel_level,
        latitude=vehicle.position.latitude,
        longitude=vehicle.position.longitude,
        speed_kmh=vehicle.speed_kmh,
        driver_id=vehicle.driver_id,
        mission_id=vehicle.mission_id,
        max_fuel=vehicle.max_fuel,
        created_at=vehicle.created_at,
        updated_at=vehicle.updated_at,
    )


class VehicleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        result = await self._session.execute(
            select(VehicleModel).where(VehicleModel.id == vehicle_id)
        )
        model = result.scalar_one_or_none()
        return _vehicle_to_domain(model) if model else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[Vehicle]:
        result = await self._session.execute(
            select(VehicleModel).offset(skip).limit(limit).order_by(VehicleModel.license_plate)
        )
        return [_vehicle_to_domain(m) for m in result.scalars().all()]

    async def get_by_state(self, state: VehicleState) -> list[Vehicle]:
        result = await self._session.execute(
            select(VehicleModel).where(VehicleModel.state == state.value)
        )
        return [_vehicle_to_domain(m) for m in result.scalars().all()]

    async def count(self) -> int:
        result = await self._session.execute(select(func.count()).select_from(VehicleModel))
        return result.scalar_one()

    async def save(self, vehicle: Vehicle) -> Vehicle:
        existing = await self._session.get(VehicleModel, vehicle.id)
        if existing:
            existing.license_plate = vehicle.license_plate
            existing.model = vehicle.model
            existing.state = vehicle.state.value
            existing.fuel_level = vehicle.fuel_level
            existing.latitude = vehicle.position.latitude
            existing.longitude = vehicle.position.longitude
            existing.speed_kmh = vehicle.speed_kmh
            existing.driver_id = vehicle.driver_id
            existing.mission_id = vehicle.mission_id
            existing.max_fuel = vehicle.max_fuel
            existing.updated_at = vehicle.updated_at
        else:
            self._session.add(_vehicle_to_model(vehicle))
        await self._session.flush()
        return vehicle

    async def bulk_save(self, vehicles: list[Vehicle]) -> None:
        for vehicle in vehicles:
            await self.save(vehicle)


def _driver_to_domain(model: VirtualDriverModel) -> VirtualDriver:
    return VirtualDriver(
        id=model.id,
        name=model.name,
        status=DriverStatus(model.status),
        vehicle_id=model.vehicle_id,
        experience_years=model.experience_years,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class VirtualDriverRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, driver_id: UUID) -> VirtualDriver | None:
        result = await self._session.execute(
            select(VirtualDriverModel).where(VirtualDriverModel.id == driver_id)
        )
        model = result.scalar_one_or_none()
        return _driver_to_domain(model) if model else None

    async def get_available(self) -> list[VirtualDriver]:
        result = await self._session.execute(
            select(VirtualDriverModel).where(VirtualDriverModel.status == "available")
        )
        return [_driver_to_domain(m) for m in result.scalars().all()]

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[VirtualDriver]:
        result = await self._session.execute(select(VirtualDriverModel).offset(skip).limit(limit))
        return [_driver_to_domain(m) for m in result.scalars().all()]

    async def save(self, driver: VirtualDriver) -> VirtualDriver:
        existing = await self._session.get(VirtualDriverModel, driver.id)
        if existing:
            existing.name = driver.name
            existing.status = driver.status.value
            existing.vehicle_id = driver.vehicle_id
            existing.experience_years = driver.experience_years
            existing.updated_at = driver.updated_at
        else:
            self._session.add(
                VirtualDriverModel(
                    id=driver.id,
                    name=driver.name,
                    status=driver.status.value,
                    vehicle_id=driver.vehicle_id,
                    experience_years=driver.experience_years,
                    created_at=driver.created_at,
                    updated_at=driver.updated_at,
                )
            )
        await self._session.flush()
        return driver
