import pytest

from alcc.worker.celery_app import celery_app
from alcc.worker.tasks import (
    compute_analytics,
    optimize_routes,
    schedule_maintenance,
    send_notification_batch,
)


@pytest.fixture(autouse=True)
def celery_eager():
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_store_eager_result = True
    yield


class TestCeleryTasks:
    def test_optimize_routes(self):
        result = optimize_routes.apply().get()
        assert result["status"] == "completed"
        assert result["missions_optimized"] >= 5
        assert result["distance_saved_km"] > 0

    def test_optimize_routes_with_mission_ids(self):
        result = optimize_routes.apply(args=(["m1", "m2", "m3"],)).get()
        assert result["status"] == "completed"

    def test_schedule_maintenance(self):
        result = schedule_maintenance.apply().get()
        assert result["status"] == "completed"
        assert result["vehicles_scheduled"] >= 1

    def test_schedule_maintenance_with_vehicle_ids(self):
        result = schedule_maintenance.apply(args=(["v1", "v2"],)).get()
        assert result["vehicles_scheduled"] == 2

    def test_compute_analytics(self):
        result = compute_analytics.apply().get()
        assert result["status"] == "completed"
        assert 0.6 <= result["fleet_utilization"] <= 0.9

    def test_send_notification_batch(self):
        result = send_notification_batch.apply(args=(["n1", "n2", "n3"],)).get()
        assert result["sent_count"] == 3
        assert result["status"] == "completed"
