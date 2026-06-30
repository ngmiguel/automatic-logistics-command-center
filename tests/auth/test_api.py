import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthAPI:
    async def test_register_success(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@alcc.io",
                "password": "password123",
                "full_name": "New User",
                "role": "operator",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@alcc.io"
        assert data["role"] == "operator"
        assert data["is_active"] is True

    async def test_register_duplicate_email(self, client: AsyncClient):
        payload = {
            "email": "dup@alcc.io",
            "password": "password123",
            "full_name": "Dup User",
            "role": "operator",
        }
        await client.post("/api/v1/auth/register", json=payload)
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 409

    async def test_register_invalid_password(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "short@alcc.io",
                "password": "short",
                "full_name": "Short",
                "role": "operator",
            },
        )
        assert response.status_code == 422

    async def test_login_success(self, client: AsyncClient):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "login@alcc.io",
                "password": "password123",
                "full_name": "Login User",
                "role": "dispatcher",
            },
        )
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "login@alcc.io", "password": "password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "dispatcher"

    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrong@alcc.io",
                "password": "password123",
                "full_name": "Wrong",
                "role": "operator",
            },
        )
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "wrong@alcc.io", "password": "badpassword"},
        )
        assert response.status_code == 401

    async def test_me_authenticated(self, client: AsyncClient, operator_headers: dict):
        response = await client.get("/api/v1/auth/me", headers=operator_headers)
        assert response.status_code == 200
        assert response.json()["email"] == "operator@test.io"

    async def test_me_unauthenticated(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 403

    async def test_me_invalid_token(self, client: AsyncClient):
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalidtoken"},
        )
        assert response.status_code == 401
