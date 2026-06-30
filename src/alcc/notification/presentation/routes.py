from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from alcc.auth.domain.entities import User
from alcc.auth.presentation.dependencies import get_current_user, require_roles
from alcc.notification.domain.entities import Incident
from alcc.notification.infrastructure.repositories import IncidentRepository, NotificationRepository
from alcc.shared.domain.enums import IncidentSeverity, UserRole
from alcc.shared.infrastructure.database.session import get_db_session

router = APIRouter(prefix="/notifications", tags=["Notifications"])


class NotificationResponse(BaseModel):
    id: UUID
    type: str
    title: str
    message: str
    severity: str
    vehicle_id: UUID | None
    is_read: bool


class IncidentResponse(BaseModel):
    id: UUID
    vehicle_id: UUID
    severity: IncidentSeverity
    description: str
    resolved: bool


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[NotificationResponse]:
    repo = NotificationRepository(session)
    notifications = await repo.get_unread()
    return [
        NotificationResponse(
            id=n.id, type=n.type.value, title=n.title, message=n.message,
            severity=n.severity.value, vehicle_id=n.vehicle_id, is_read=n.is_read,
        )
        for n in notifications
    ]


@router.post("/{notification_id}/read", status_code=204)
async def mark_notification_read(
    notification_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> None:
    repo = NotificationRepository(session)
    await repo.mark_read(notification_id)


@router.get("/incidents", response_model=list[IncidentResponse])
async def list_incidents(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> list[IncidentResponse]:
    repo = IncidentRepository(session)
    incidents = await repo.get_open()
    return [
        IncidentResponse(
            id=i.id, vehicle_id=i.vehicle_id, severity=i.severity,
            description=i.description, resolved=i.resolved,
        )
        for i in incidents
    ]


@router.post("/incidents/{incident_id}/resolve", response_model=IncidentResponse)
async def resolve_incident(
    incident_id: UUID,
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles(UserRole.OPERATOR, UserRole.ADMIN)),
) -> IncidentResponse:
    repo = IncidentRepository(session)
    from sqlalchemy import select
    from alcc.shared.infrastructure.database.models import IncidentModel
    result = await session.execute(
        select(IncidentModel).where(IncidentModel.id == incident_id)
    )
    model = result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Incident not found")
    incident = Incident(
        id=model.id, vehicle_id=model.vehicle_id,
        severity=IncidentSeverity(model.severity),
        description=model.description, resolved=model.resolved,
        created_at=model.created_at, updated_at=model.updated_at,
    )
    incident.resolve()
    model.resolved = True
    model.resolved_at = incident.resolved_at
    await session.flush()
    return IncidentResponse(
        id=incident.id, vehicle_id=incident.vehicle_id, severity=incident.severity,
        description=incident.description, resolved=incident.resolved,
    )
