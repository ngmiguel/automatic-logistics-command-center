from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from alcc.notification.domain.entities import Incident, Notification
from alcc.shared.domain.enums import IncidentSeverity, NotificationType
from alcc.shared.infrastructure.database.models import IncidentModel, NotificationModel


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, notification: Notification) -> Notification:
        self._session.add(
            NotificationModel(
                id=notification.id,
                type=notification.type.value,
                title=notification.title,
                message=notification.message,
                severity=notification.severity.value,
                vehicle_id=notification.vehicle_id,
                mission_id=notification.mission_id,
                is_read=notification.is_read,
                read_at=notification.read_at,
                created_at=notification.created_at,
                updated_at=notification.updated_at,
            )
        )
        await self._session.flush()
        return notification

    async def get_unread(self, limit: int = 50) -> list[Notification]:
        result = await self._session.execute(
            select(NotificationModel)
            .where(NotificationModel.is_read.is_(False))
            .order_by(NotificationModel.created_at.desc())
            .limit(limit)
        )
        return [
            Notification(
                id=m.id,
                type=NotificationType(m.type),
                title=m.title,
                message=m.message,
                severity=IncidentSeverity(m.severity),
                vehicle_id=m.vehicle_id,
                mission_id=m.mission_id,
                is_read=m.is_read,
                read_at=m.read_at,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in result.scalars().all()
        ]

    async def mark_read(self, notification_id: UUID) -> None:
        model = await self._session.get(NotificationModel, notification_id)
        if model:
            model.is_read = True
            await self._session.flush()


class IncidentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, incident: Incident) -> Incident:
        self._session.add(
            IncidentModel(
                id=incident.id,
                vehicle_id=incident.vehicle_id,
                severity=incident.severity.value,
                description=incident.description,
                resolved=incident.resolved,
                resolved_at=incident.resolved_at,
                created_at=incident.created_at,
                updated_at=incident.updated_at,
            )
        )
        await self._session.flush()
        return incident

    async def get_open(self) -> list[Incident]:
        result = await self._session.execute(
            select(IncidentModel).where(IncidentModel.resolved.is_(False))
        )
        return [
            Incident(
                id=m.id,
                vehicle_id=m.vehicle_id,
                severity=IncidentSeverity(m.severity),
                description=m.description,
                resolved=m.resolved,
                resolved_at=m.resolved_at,
                created_at=m.created_at,
                updated_at=m.updated_at,
            )
            for m in result.scalars().all()
        ]

    async def count_open(self) -> int:
        result = await self._session.execute(
            select(IncidentModel).where(IncidentModel.resolved.is_(False))
        )
        return len(result.scalars().all())
