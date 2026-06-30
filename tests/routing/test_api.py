import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRoutingAPI:
    async def _setup_vehicle_with_driver(
        self, client: AsyncClient, operator_headers: dict, dispatcher_headers: dict
    ) -> str:
        vehicle = await client.post(
            "/api/v1/fleet/vehicles",
            json={"license_plate": "ALC-ROUTE-01", "model": "X1"},
            headers=operator_headers,
        )
        driver = await client.post(
            "/api/v1/fleet/drivers",
            json={"name": "Route Driver", "experience_years": 4},
            headers=operator_headers,
        )
        await client.post(
            f"/api/v1/fleet/vehicles/{vehicle.json()['id']}/assign-driver",
            json={"driver_id": driver.json()["id"]},
            headers=dispatcher_headers,
        )
        return vehicle.json()["id"]

    async def test_create_mission(self, client: AsyncClient, dispatcher_headers: dict):
        response = await client.post(
            "/api/v1/missions",
            json={
                "origin_lat": 48.8566,
                "origin_lng": 2.3522,
                "dest_lat": 51.5074,
                "dest_lng": -0.1278,
                "priority": 2,
                "cargo_description": "Electronics",
            },
            headers=dispatcher_headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert data["estimated_distance_km"] > 0

    async def test_create_mission_forbidden_for_operator(
        self, client: AsyncClient, operator_headers: dict
    ):
        response = await client.post(
            "/api/v1/missions",
            json={"origin_lat": 0, "origin_lng": 0, "dest_lat": 1, "dest_lng": 1},
            headers=operator_headers,
        )
        assert response.status_code == 403

    async def test_list_missions(self, client: AsyncClient, dispatcher_headers: dict):
        await client.post(
            "/api/v1/missions",
            json={"origin_lat": 0, "origin_lng": 0, "dest_lat": 1, "dest_lng": 1},
            headers=dispatcher_headers,
        )
        response = await client.get("/api/v1/missions", headers=dispatcher_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    async def test_assign_and_complete_mission(
        self,
        client: AsyncClient,
        dispatcher_headers: dict,
        operator_headers: dict,
    ):
        mission = await client.post(
            "/api/v1/missions",
            json={"origin_lat": 48.0, "origin_lng": 2.0, "dest_lat": 49.0, "dest_lng": 3.0},
            headers=dispatcher_headers,
        )
        mission_id = mission.json()["id"]
        vehicle_id = await self._setup_vehicle_with_driver(
            client, operator_headers, dispatcher_headers
        )
        assign = await client.post(
            f"/api/v1/missions/{mission_id}/assign",
            json={"vehicle_id": vehicle_id},
            headers=dispatcher_headers,
        )
        assert assign.status_code == 200
        assert assign.json()["status"] == "in_progress"

        complete = await client.post(
            f"/api/v1/missions/{mission_id}/complete",
            headers=dispatcher_headers,
        )
        assert complete.status_code == 200
        assert complete.json()["status"] == "completed"

    async def test_cancel_mission(self, client: AsyncClient, dispatcher_headers: dict):
        mission = await client.post(
            "/api/v1/missions",
            json={"origin_lat": 0, "origin_lng": 0, "dest_lat": 1, "dest_lng": 1},
            headers=dispatcher_headers,
        )
        mission_id = mission.json()["id"]
        response = await client.post(
            f"/api/v1/missions/{mission_id}/cancel",
            headers=dispatcher_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "cancelled"

    async def test_get_mission_not_found(self, client: AsyncClient, dispatcher_headers: dict):
        response = await client.get(
            "/api/v1/missions/00000000-0000-0000-0000-000000000001",
            headers=dispatcher_headers,
        )
        assert response.status_code == 404
