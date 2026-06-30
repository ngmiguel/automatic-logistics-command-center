import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_dashboard_html(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert "Command Center" in response.text


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    register = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@alcc.io",
            "password": "testpass123",
            "full_name": "Test User",
            "role": "operator",
        },
    )
    assert register.status_code == 201

    login = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@alcc.io", "password": "testpass123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert token

    me = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me.status_code == 200
    assert me.json()["email"] == "test@alcc.io"
