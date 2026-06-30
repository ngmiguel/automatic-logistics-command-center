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

    def test_assign_driver_in_maintenance_fails(self):
        vehicle = Vehicle(license_plate="ALC-0001", state=VehicleState.MAINTENANCE)
        with pytest.raises(ValidationError):
            vehicle.assign_driver(uuid4())

    def test_assign_mission_requires_driver(self):
        vehicle = Vehicle(license_plate="ALC-0001")
        with pytest.raises(ValidationError, match="assigned driver"):
            vehicle.assign_mission(uuid4())

    def test_assign_mission_requires_idle(self):
        vehicle = Vehicle(license_plate="ALC-0001", state=VehicleState.EN_ROUTE)
        vehicle.driver_id = uuid4()
        with pytest.raises(ValidationError, match="idle"):
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
        assert vehicle.speed_kmh == 0.0

    def test_enter_maintenance(self):
        vehicle = Vehicle(license_plate="ALC-0001")
        vehicle.enter_maintenance()
        assert vehicle.state == VehicleState.MAINTENANCE

    def test_enter_maintenance_while_en_route_fails(self):
        vehicle = Vehicle(license_plate="ALC-0001", state=VehicleState.EN_ROUTE)
        with pytest.raises(ValidationError):
            vehicle.enter_maintenance()

    def test_trigger_and_resolve_incident(self):
        vehicle = Vehicle(license_plate="ALC-0001")
        vehicle.trigger_incident()
        assert vehicle.state == VehicleState.INCIDENT
        vehicle.resolve_incident()
        assert vehicle.state == VehicleState.IDLE

    def test_fuel_depletion_triggers_incident(self):
        vehicle = Vehicle(license_plate="ALC-0001", fuel_level=1.0)
        vehicle.assign_driver(uuid4())
        vehicle.assign_mission(uuid4())
        vehicle.consume_fuel(5.0)
        assert vehicle.state == VehicleState.INCIDENT
        assert vehicle.fuel_level == 0.0

    def test_refuel_caps_at_max(self):
        vehicle = Vehicle(license_plate="ALC-0001", fuel_level=90.0, max_fuel=100.0)
        vehicle.refuel(20.0)
        assert vehicle.fuel_level == 100.0

    def test_update_telemetry(self):
        vehicle = Vehicle(license_plate="ALC-0001")
        vehicle.update_telemetry(48.8566, 2.3522, 60.0)
        assert vehicle.position.latitude == 48.8566
        assert vehicle.speed_kmh == 60.0

    def test_state_change_emits_event(self):
        vehicle = Vehicle(license_plate="ALC-0001")
        vehicle.trigger_incident()
        events = vehicle.pull_events()
        assert any(e.event_type == "vehicle.state_changed" for e in events)

    def test_geo_position_validation(self):
        with pytest.raises(ValidationError):
            GeoPosition(100.0, 0.0)
        with pytest.raises(ValidationError):
            GeoPosition(0.0, 200.0)


class TestVirtualDriver:
    def test_assign_and_release(self):
        driver = VirtualDriver(name="Driver-001")
        vehicle_id = uuid4()
        driver.assign_to_vehicle(vehicle_id)
        assert driver.status == DriverStatus.ASSIGNED
        assert driver.vehicle_id == vehicle_id
        driver.release()
        assert driver.status == DriverStatus.AVAILABLE
        assert driver.vehicle_id is None

    def test_cannot_assign_unavailable_driver(self):
        driver = VirtualDriver(name="Driver-002")
        driver.assign_to_vehicle(uuid4())
        with pytest.raises(ValidationError):
            driver.assign_to_vehicle(uuid4())
