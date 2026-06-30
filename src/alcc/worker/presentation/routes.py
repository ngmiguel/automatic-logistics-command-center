from fastapi import APIRouter, Depends

from alcc.auth.domain.entities import User
from alcc.auth.presentation.dependencies import require_roles
from alcc.shared.domain.enums import UserRole
from alcc.worker.tasks import compute_analytics, optimize_routes, schedule_maintenance

router = APIRouter(prefix="/tasks", tags=["Async Tasks"])


@router.post("/optimize-routes")
async def trigger_route_optimization(
    _: User = Depends(require_roles(UserRole.DISPATCHER, UserRole.ADMIN)),
) -> dict:
    task = optimize_routes.delay()
    return {"task_id": task.id, "status": "queued"}


@router.post("/schedule-maintenance")
async def trigger_maintenance_schedule(
    _: User = Depends(require_roles(UserRole.OPERATOR, UserRole.ADMIN)),
) -> dict:
    task = schedule_maintenance.delay()
    return {"task_id": task.id, "status": "queued"}


@router.post("/compute-analytics")
async def trigger_analytics_computation(
    _: User = Depends(require_roles(UserRole.ANALYST, UserRole.ADMIN)),
) -> dict:
    task = compute_analytics.delay()
    return {"task_id": task.id, "status": "queued"}


@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    _: User = Depends(require_roles(UserRole.ADMIN)),
) -> dict:
    from alcc.worker.celery_app import celery_app

    result = celery_app.AsyncResult(task_id)
    return {"task_id": task_id, "status": result.status, "result": result.result}
