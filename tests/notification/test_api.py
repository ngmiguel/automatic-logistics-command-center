from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from alcc.notification.domain.entities import Incident, Notification
from alcc.notification.infrastructure.repositories import IncidentRepository, NotificationRepository
from alcc.shared.domain.enums import IncidentSeverity, NotificationType


@pytest.mark.asyncio
class TestNotificationRepository:
    async def test_save_and_get_unread(self, db_session: AsyncSession):
        repo = NotificationRepository(db_session)
        notif = Notification(
            type=NotificationType.SYSTEM,
            title="Alert",
            message="Test alert",
            severity=IncidentSeverity.LOW,
        )
        await repo.save(notif)
        unread = await repo.get_unread()
        assert len(unread) >= 1

    async def test_mark_read(self, db_session: AsyncSession):
        repo = NotificationRepository(db_session)
        notif = Notification(title="Read me", message="msg")
        await repo.save(notif)
        await repo.mark_read(notif.id)
        unread = await repo.get_unread()
        assert all(n.id != notif.id for n in unread)


@pytest.mark.asyncio
class TestIncidentRepository:
    async def test_save_and_get_open(self, db_session: AsyncSession):
        repo = IncidentRepository(db_session)
        incident = Incident(
            vehicle_id=uuid4(),
            severity=IncidentSeverity.HIGH,
            description="Tire blowout",
        )
        await repo.save(incident)
        open_incidents = await repo.get_open()
        assert len(open_incidents) >= 1

    async def test_count_open(self, db_session: AsyncSession):
        repo = IncidentRepository(db_session)
        await repo.save(Incident(vehicle_id=uuid4(), description="Test"))
        assert await repo.count_open() >= 1


@pytest.mark.asyncio
class TestNotificationAPI:
    async def test_list_notifications(self, client: AsyncClient, operator_headers: dict, db_session: AsyncSession):
        repo = NotificationRepository(db_session)
        await repo.save(Notification(title="API Test", message="From test"))
        await db_session.commit()
        response = await client.get("/api/v1/notifications", headers=operator_headers)
        assert response.status_code == 200

    async def test_list_incidents(self, client: AsyncClient, operator_headers: dict, db_session: AsyncSession):
        repo = IncidentRepository(db_session)
        await repo.save(Incident(vehicle_id=uuid4(), description="Open incident"))
        await db_session.commit()
        response = await client.get("/api/v1/notifications/incidents", headers=operator_headers)
        assert response.status_code == 200
        assert len(response.json()) >= 1

    async def test_resolve_incident(
        self, client: AsyncClient, operator_headers: dict, db_session: AsyncSession
    ):
        repo = IncidentRepository(db_session)
        incident = Incident(vehicle_id=uuid4(), description="To resolve")
        await repo.save(incident)
        await db_session.commit()
        response = await client.post(
            f"/api/v1/notifications/incidents/{incident.id}/resolve",
            headers=operator_headers,
        )
        assert response.status_code == 200
        assert response.json()["resolved"] is True

    async def test_resolve_incident_not_found(self, client: AsyncClient, operator_headers: dict):
        response = await client.post(
            f"/api/v1/notifications/incidents/{uuid4()}/resolve",
            headers=operator_headers,
        )
        assert response.status_code == 404
