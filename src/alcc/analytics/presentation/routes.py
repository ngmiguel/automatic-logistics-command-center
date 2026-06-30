from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from alcc.analytics.domain.entities import FleetKPIs, IncidentKPIs, MissionKPIs
from alcc.auth.domain.entities import User
from alcc.auth.presentation.dependencies import get_current_user, require_roles
from alcc.fleet.infrastructure.repositories import VehicleRepository
from alcc.notification.infrastructure.repositories import IncidentRepository
from alcc.routing.infrastructure.repositories import MissionRepository
from alcc.shared.domain.enums import MissionStatus, UserRole, VehicleState
from alcc.shared.infrastructure.database.session import get_db_session

router = APIRouter(prefix="/analytics", tags=["Analytics"])


async def _compute_fleet_kpis(session: AsyncSession) -> dict:
    repo = VehicleRepository(session)
    total = await repo.count()
    by_state: dict[str, int] = {}
    fuel_sum = 0.0
    speed_sum = 0.0
    active = 0
    for state in VehicleState:
        vehicles = await repo.get_by_state(state)
        by_state[state.value] = len(vehicles)
        for v in vehicles:
            fuel_sum += v.fuel_level
            speed_sum += v.speed_kmh
            if state == VehicleState.EN_ROUTE:
                active += 1
    kpis = FleetKPIs(
        total_vehicles=total,
        active_vehicles=active,
        idle_vehicles=by_state.get("idle", 0),
        en_route_vehicles=by_state.get("en_route", 0),
        maintenance_vehicles=by_state.get("maintenance", 0),
        incident_vehicles=by_state.get("incident", 0),
        offline_vehicles=by_state.get("offline", 0),
        fleet_utilization_rate=active / total if total else 0.0,
        average_fuel_level=fuel_sum / total if total else 0,
        average_speed_kmh=speed_sum / total if total else 0,
    )
    return kpis.to_dict()


async def _compute_mission_kpis(session: AsyncSession) -> dict:
    repo = MissionRepository(session)
    counts = {s.value: len(await repo.get_by_status(s)) for s in MissionStatus}
    total = sum(counts.values())
    completed = counts.get("completed", 0)
    kpis = MissionKPIs(
        total_missions=total,
        pending=counts.get("pending", 0),
        in_progress=counts.get("in_progress", 0),
        completed=completed,
        cancelled=counts.get("cancelled", 0),
        failed=counts.get("failed", 0),
        completion_rate=completed / total if total else 0,
    )
    return kpis.to_dict()


async def _compute_incident_kpis(session: AsyncSession) -> dict:
    repo = IncidentRepository(session)
    open_incidents = await repo.get_open()
    critical = sum(1 for i in open_incidents if i.severity.value == "critical")
    total_open = len(open_incidents)
    kpis = IncidentKPIs(
        total_incidents=total_open,
        open_incidents=total_open,
        resolved_incidents=0,
        critical_incidents=critical,
        incident_rate=total_open / 1000,
    )
    return kpis.to_dict()


@router.get("/fleet")
async def fleet_analytics(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles(UserRole.ANALYST, UserRole.OPERATOR, UserRole.ADMIN)),
) -> dict:
    return await _compute_fleet_kpis(session)


@router.get("/missions")
async def mission_analytics(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles(UserRole.ANALYST, UserRole.ADMIN)),
) -> dict:
    return await _compute_mission_kpis(session)


@router.get("/incidents")
async def incident_analytics(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_roles(UserRole.ANALYST, UserRole.ADMIN)),
) -> dict:
    return await _compute_incident_kpis(session)


@router.get("/public/summary")
async def public_summary(
    session: AsyncSession = Depends(get_db_session),
) -> dict:
    """Public KPI summary for the embedded command center dashboard."""
    return {
        "fleet": await _compute_fleet_kpis(session),
        "missions": await _compute_mission_kpis(session),
        "incidents": await _compute_incident_kpis(session),
    }


@router.get("/dashboard")
async def full_dashboard(
    session: AsyncSession = Depends(get_db_session),
    _: User = Depends(get_current_user),
) -> dict:
    return {
        "fleet": await _compute_fleet_kpis(session),
        "missions": await _compute_mission_kpis(session),
        "incidents": await _compute_incident_kpis(session),
    }
