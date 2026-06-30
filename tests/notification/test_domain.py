from uuid import uuid4

from alcc.notification.domain.entities import Incident, Notification
from alcc.shared.domain.enums import IncidentSeverity, NotificationType


class TestNotificationDomain:
    def test_mark_read(self):
        notif = Notification(title="Test", message="Hello")
        assert notif.is_read is False
        notif.mark_read()
        assert notif.is_read is True
        assert notif.read_at is not None

    def test_publish_emits_event(self):
        notif = Notification(
            type=NotificationType.INCIDENT,
            title="Incident",
            message="Breakdown",
            severity=IncidentSeverity.HIGH,
        )
        notif.publish()
        events = notif.pull_events()
        assert len(events) == 1
        assert events[0].event_type == "notification.sent"

    def test_incident_resolve(self):
        incident = Incident(
            vehicle_id=uuid4(),
            severity=IncidentSeverity.CRITICAL,
            description="Engine failure",
        )
        assert incident.resolved is False
        incident.resolve()
        assert incident.resolved is True
        assert incident.resolved_at is not None

    def test_notification_with_vehicle_reference(self):
        vid = uuid4()
        notif = Notification(
            type=NotificationType.LOW_FUEL,
            title="Low fuel",
            message="Fuel at 8%",
            vehicle_id=vid,
        )
        assert notif.vehicle_id == vid
        assert notif.type == NotificationType.LOW_FUEL
