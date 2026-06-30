import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestFleetAPI:
    async def test_create_vehicle(self, client: AsyncClient, operator_headers: dict):
        response = await client.post(
            "/api/v1/fleet/vehicles",
            json={"license_plate": "ALC-TEST-01", "model": "AutoTruck X1", "latitude": 48.85, "longitude": 2.35},
            headers=operator_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["license_plate"] == "ALC-TEST-01"
        assert data["state"] == "idle"

    async def test_create_vehicle_unauthorized(self, client: AsyncClient, analyst_headers: dict):
        response = await client.post(
            "/api/v1/fleet/vehicles",
            json={"license_plate": "ALC-FAIL", "model": "X1"},
            headers=analyst_headers,
        )
        assert response.status_code == 403

    async def test_list_vehicles(self, client: AsyncClient, operator_headers: dict):
        await client.post(
            "/api/v1/fleet/vehicles",
            json={"license_plate": "ALC-LIST-01", "model": "X1"},
            headers=operator_headers,
        )
        response = await client.get("/api/v1/fleet/vehicles", headers=operator_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    async def test_get_vehicle_by_id(self, client: AsyncClient, operator_headers: dict):
        create = await client.post(
            "/api/v1/fleet/vehicles",
            json={"license_plate": "ALC-GET-01", "model": "X1"},
            headers=operator_headers,
        )
        vehicle_id = create.json()["id"]
        response = await client.get(f"/api/v1/fleet/vehicles/{vehicle_id}", headers=operator_headers)
        assert response.status_code == 200
        assert response.json()["id"] == vehicle_id

    async def test_get_vehicle_not_found(self, client: AsyncClient, operator_headers: dict):
        response = await client.get(
            "/api/v1/fleet/vehicles/00000000-0000-0000-0000-000000000001",
            headers=operator_headers,
        )
        assert response.status_code == 404

    async def test_create_driver(self, client: AsyncClient, operator_headers: dict):
        response = await client.post(
            "/api/v1/fleet/drivers",
            json={"name": "Virtual Driver 1", "experience_years": 5},
            headers=operator_headers,
        )
        assert response.status_code == 201
        assert response.json()["status"] == "available"

    async def test_list_drivers(self, client: AsyncClient, operator_headers: dict):
        await client.post(
            "/api/v1/fleet/drivers",
            json={"name": "Driver List", "experience_years": 3},
            headers=operator_headers,
        )
        response = await client.get("/api/v1/fleet/drivers", headers=operator_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    async def test_assign_driver_to_vehicle(
        self, client: AsyncClient, dispatcher_headers: dict, operator_headers: dict
    ):
        vehicle = await client.post(
            "/api/v1/fleet/vehicles",
            json={"license_plate": "ALC-ASSIGN-01", "model": "X1"},
            headers=operator_headers,
        )
        driver = await client.post(
            "/api/v1/fleet/drivers",
            json={"name": "Assign Driver", "experience_years": 2},
            headers=operator_headers,
        )
        response = await client.post(
            f"/api/v1/fleet/vehicles/{vehicle.json()['id']}/assign-driver",
            json={"driver_id": driver.json()["id"]},
            headers=dispatcher_headers,
        )
        assert response.status_code == 200
        assert response.json()["driver_id"] == driver.json()["id"]

    async def test_fleet_stats(self, client: AsyncClient, operator_headers: dict):
        response = await client.get("/api/v1/fleet/stats", headers=operator_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_state" in data

    async def test_update_vehicle_state_to_maintenance(
        self, client: AsyncClient, operator_headers: dict
    ):
        create = await client.post(
            "/api/v1/fleet/vehicles",
            json={"license_plate": "ALC-MAINT-01", "model": "X1"},
            headers=operator_headers,
        )
        vehicle_id = create.json()["id"]
        response = await client.patch(
            f"/api/v1/fleet/vehicles/{vehicle_id}/state",
            json={"state": "maintenance"},
            headers=operator_headers,
        )
        assert response.status_code == 200
        assert response.json()["state"] == "maintenance"
