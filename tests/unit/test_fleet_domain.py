from uuid import uuid4

import pytest

from alcc.fleet.domain.entities import GeoPosition, Vehicle, VirtualDriver
from alcc.shared.domain.enums import DriverStatus, VehicleState
from alcc.shared.domain.exceptions import ValidationError


class TestVehicle:
    def test_register_vehicle(self):
        vehicle = Vehicle(license_plate="ALC-0001")
        vehicle.register()
        assert vehicle.state == VehicleState.IDLE
        assert len(vehicle.pull_events()) == 1

    def test_assign_driver(self):
        vehicle = Vehicle(license_plate="ALC-0001")
        driver_id = uuid4()
        vehicle.assign_driver(driver_id)
        assert vehicle.driver_id == driver_id

    def test_assign_mission_requires_driver(self):
        vehicle = Vehicle(license_plate="ALC-0001")
        with pytest.raises(ValidationError):
            vehicle.assign_mission(uuid4())

    def test_mission_lifecycle(self):
        vehicle = Vehicle(license_plate="ALC-0001")
        vehicle.assign_driver(uuid4())
        mission_id = uuid4()
        vehicle.assign_mission(mission_id)
        assert vehicle.state == VehicleState.EN_ROUTE
        assert vehicle.mission_id == mission_id
        vehicle.complete_mission()
        assert vehicle.state == VehicleState.IDLE
        assert vehicle.mission_id is None

    def test_fuel_depletion_triggers_incident(self):
        vehicle = Vehicle(license_plate="ALC-0001", fuel_level=1.0)
        vehicle.assign_driver(uuid4())
        vehicle.assign_mission(uuid4())
        vehicle.consume_fuel(5.0)
        assert vehicle.state == VehicleState.INCIDENT
        assert vehicle.fuel_level == 0.0

    def test_geo_position_validation(self):
        with pytest.raises(ValidationError):
            GeoPosition(100.0, 0.0)


class TestVirtualDriver:
    def test_assign_and_release(self):
        driver = VirtualDriver(name="Driver-001")
        vehicle_id = uuid4()
        driver.assign_to_vehicle(vehicle_id)
        assert driver.status == DriverStatus.ASSIGNED
        driver.release()
        assert driver.status == DriverStatus.AVAILABLE

    def test_cannot_assign_unavailable_driver(self):
        driver = VirtualDriver(name="Driver-002")
        driver.assign_to_vehicle(uuid4())
        with pytest.raises(ValidationError):
            driver.assign_to_vehicle(uuid4())
