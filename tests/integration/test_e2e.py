import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestHealthAndMetrics:
    async def test_health_endpoint(self, client: AsyncClient):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    async def test_metrics_endpoint(self, client: AsyncClient):
        response = await client.get("/metrics")
        assert response.status_code == 200
        assert "alcc_http_requests_total" in response.text or len(response.content) > 0

    async def test_dashboard_html(self, client: AsyncClient):
        response = await client.get("/")
        assert response.status_code == 200
        assert "Command Center" in response.text
        assert "WebSocket" in response.text or "ws" in response.text


@pytest.mark.asyncio
class TestEndToEndFlow:
    async def test_full_dispatch_flow(
        self,
        client: AsyncClient,
        operator_headers: dict,
        dispatcher_headers: dict,
    ):
        vehicle_resp = await client.post(
            "/api/v1/fleet/vehicles",
            json={"license_plate": "E2E-001", "model": "AutoTruck", "latitude": 48.85, "longitude": 2.35},
            headers=operator_headers,
        )
        assert vehicle_resp.status_code == 201
        vehicle_id = vehicle_resp.json()["id"]

        driver_resp = await client.post(
            "/api/v1/fleet/drivers",
            json={"name": "E2E Driver", "experience_years": 5},
            headers=operator_headers,
        )
        driver_id = driver_resp.json()["id"]

        assign_driver = await client.post(
            f"/api/v1/fleet/vehicles/{vehicle_id}/assign-driver",
            json={"driver_id": driver_id},
            headers=dispatcher_headers,
        )
        assert assign_driver.status_code == 200

        mission_resp = await client.post(
            "/api/v1/missions",
            json={
                "origin_lat": 48.85,
                "origin_lng": 2.35,
                "dest_lat": 51.50,
                "dest_lng": -0.12,
                "cargo_description": "E2E cargo",
            },
            headers=dispatcher_headers,
        )
        assert mission_resp.status_code == 201
        mission_id = mission_resp.json()["id"]

        assign_mission = await client.post(
            f"/api/v1/missions/{mission_id}/assign",
            json={"vehicle_id": vehicle_id},
            headers=dispatcher_headers,
        )
        assert assign_mission.status_code == 200
        assert assign_mission.json()["status"] == "in_progress"

        vehicle_check = await client.get(
            f"/api/v1/fleet/vehicles/{vehicle_id}",
            headers=operator_headers,
        )
        assert vehicle_check.json()["state"] == "en_route"

        complete = await client.post(
            f"/api/v1/missions/{mission_id}/complete",
            headers=dispatcher_headers,
        )
        assert complete.status_code == 200
        assert complete.json()["status"] == "completed"

        final_vehicle = await client.get(
            f"/api/v1/fleet/vehicles/{vehicle_id}",
            headers=operator_headers,
        )
        assert final_vehicle.json()["state"] == "idle"

    async def test_analytics_after_fleet_operations(
        self, client: AsyncClient, operator_headers: dict
    ):
        await client.post(
            "/api/v1/fleet/vehicles",
            json={"license_plate": "E2E-ANALYTICS", "model": "X1"},
            headers=operator_headers,
        )
        summary = await client.get("/api/v1/analytics/public/summary")
        assert summary.status_code == 200
        assert summary.json()["fleet"]["total_vehicles"] >= 1
