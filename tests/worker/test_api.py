import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestWorkerAPI:
    async def test_trigger_route_optimization(self, client: AsyncClient, dispatcher_headers: dict):
        response = await client.post(
            "/api/v1/tasks/optimize-routes",
            headers=dispatcher_headers,
        )
        assert response.status_code == 200
        assert response.json()["status"] == "queued"

    async def test_trigger_maintenance(self, client: AsyncClient, operator_headers: dict):
        response = await client.post(
            "/api/v1/tasks/schedule-maintenance",
            headers=operator_headers,
        )
        assert response.status_code == 200

    async def test_trigger_analytics(self, client: AsyncClient, analyst_headers: dict):
        response = await client.post(
            "/api/v1/tasks/compute-analytics",
            headers=analyst_headers,
        )
        assert response.status_code == 200

    async def test_optimize_routes_forbidden_for_operator(
        self, client: AsyncClient, operator_headers: dict
    ):
        response = await client.post(
            "/api/v1/tasks/optimize-routes",
            headers=operator_headers,
        )
        assert response.status_code == 403
