import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAnalyticsAPI:
    async def test_public_summary(self, client: AsyncClient):
        response = await client.get("/api/v1/analytics/public/summary")
        assert response.status_code == 200
        data = response.json()
        assert "fleet" in data
        assert "missions" in data
        assert "incidents" in data

    async def test_fleet_analytics(self, client: AsyncClient, analyst_headers: dict):
        response = await client.get("/api/v1/analytics/fleet", headers=analyst_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_vehicles" in data
        assert "fleet_utilization_rate" in data

    async def test_fleet_analytics_forbidden_for_dispatcher(
        self, client: AsyncClient, dispatcher_headers: dict
    ):
        response = await client.get("/api/v1/analytics/fleet", headers=dispatcher_headers)
        assert response.status_code == 403

    async def test_mission_analytics(self, client: AsyncClient, analyst_headers: dict):
        response = await client.get("/api/v1/analytics/missions", headers=analyst_headers)
        assert response.status_code == 200
        assert "completion_rate" in response.json()

    async def test_incident_analytics(self, client: AsyncClient, analyst_headers: dict):
        response = await client.get("/api/v1/analytics/incidents", headers=analyst_headers)
        assert response.status_code == 200
        assert "open_incidents" in response.json()

    async def test_dashboard(self, client: AsyncClient, operator_headers: dict):
        response = await client.get("/api/v1/analytics/dashboard", headers=operator_headers)
        assert response.status_code == 200
        data = response.json()
        assert all(k in data for k in ("fleet", "missions", "incidents"))
