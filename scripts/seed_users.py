import asyncio

from alcc.auth.domain.entities import User
from alcc.auth.infrastructure.repositories import UserRepository
from alcc.auth.infrastructure.security import hash_password
from alcc.shared.domain.enums import UserRole
from alcc.shared.infrastructure.database.session import get_session_factory, init_db
from alcc.shared.infrastructure.logging import setup_logging

DEFAULT_USERS = [
    ("admin@alcc.io", "admin1234", "System Admin", UserRole.ADMIN),
    ("dispatcher@alcc.io", "dispatch123", "Lead Dispatcher", UserRole.DISPATCHER),
    ("operator@alcc.io", "operator123", "Fleet Operator", UserRole.OPERATOR),
    ("analyst@alcc.io", "analyst123", "Data Analyst", UserRole.ANALYST),
]


async def seed_users() -> None:
    setup_logging(debug=True)
    await init_db()
    async with get_session_factory()() as session:
        repo = UserRepository(session)
        for email, password, name, role in DEFAULT_USERS:
            existing = await repo.get_by_email(email)
            if not existing:
                user = User(
                    email=email,
                    hashed_password=hash_password(password),
                    full_name=name,
                    role=role,
                )
                await repo.save(user)
                print(f"Created user: {email} ({role.value})")
            else:
                print(f"User exists: {email}")
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_users())
