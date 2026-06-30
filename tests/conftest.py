import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

os.environ.setdefault("TESTING", "true")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from alcc.main import app  # noqa: E402
from alcc.shared.infrastructure.database.session import get_engine, get_session_factory, init_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield
    engine = get_engine()
    async with engine.begin() as conn:
        from alcc.shared.infrastructure.database.models import Base

        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    factory = get_session_factory()
    async with factory() as session:
        yield session
        await session.commit()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


async def register_and_login(
    client: AsyncClient,
    email: str,
    password: str,
    role: str = "operator",
    full_name: str = "Test User",
) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": full_name, "role": role},
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return login.json()["access_token"]


@pytest_asyncio.fixture
async def operator_headers(client: AsyncClient) -> dict[str, str]:
    token = await register_and_login(client, "operator@test.io", "operator123", "operator")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def dispatcher_headers(client: AsyncClient) -> dict[str, str]:
    token = await register_and_login(client, "dispatcher@test.io", "dispatch123", "dispatcher")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(client: AsyncClient) -> dict[str, str]:
    token = await register_and_login(client, "admin@test.io", "admin1234", "admin")
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def analyst_headers(client: AsyncClient) -> dict[str, str]:
    token = await register_and_login(client, "analyst@test.io", "analyst123", "analyst")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def celery_eager_mode():
    from alcc.worker.celery_app import celery_app

    celery_app.conf.task_always_eager = True
    celery_app.conf.task_store_eager_result = True
    yield


@pytest.fixture
def mock_redis(monkeypatch):
    store: dict[str, str] = {}

    async def publish_telemetry(data: dict) -> None:
        store[data["vehicle_id"]] = __import__("json").dumps(data)

    async def get_telemetry(vehicle_id: str) -> dict | None:
        raw = store.get(vehicle_id)
        return __import__("json").loads(raw) if raw else None

    async def get_all_telemetry_keys() -> list[str]:
        return list(store.keys())

    async def connect() -> None:
        pass

    async def disconnect() -> None:
        pass

    from alcc.shared.infrastructure import redis_client as rc

    monkeypatch.setattr(rc.redis_client, "publish_telemetry", publish_telemetry)
    monkeypatch.setattr(rc.redis_client, "get_telemetry", get_telemetry)
    monkeypatch.setattr(rc.redis_client, "get_all_telemetry_keys", get_all_telemetry_keys)
    monkeypatch.setattr(rc.redis_client, "connect", connect)
    monkeypatch.setattr(rc.redis_client, "disconnect", disconnect)
    return store
