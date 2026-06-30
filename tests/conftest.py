import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["SECRET_KEY"] = "test-secret-key"

from alcc.main import app  # noqa: E402
from alcc.shared.infrastructure.database.session import get_engine, init_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield
    engine = get_engine()
    async with engine.begin() as conn:
        from alcc.shared.infrastructure.database.models import Base

        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
