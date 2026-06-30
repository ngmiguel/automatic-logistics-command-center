from uuid import uuid4

from alcc.shared.domain.base import AggregateRoot, DomainEvent, Entity, Result
from alcc.shared.domain.exceptions import (
    AuthorizationError,
    ConflictError,
    DomainException,
    NotFoundError,
    ValidationError,
)


class TestDomainBase:
    def test_entity_has_uuid(self):
        entity = Entity()
        assert entity.id is not None
        assert entity.created_at is not None

    def test_aggregate_root_events(self):
        agg = AggregateRoot()
        event = DomainEvent(event_type="test.event", aggregate_id=agg.id)
        agg._register_event(event)
        events = agg.pull_events()
        assert len(events) == 1
        assert events[0].event_type == "test.event"
        assert agg.pull_events() == []

    def test_result_ok(self):
        result = Result.ok("value")
        assert result.is_success
        assert not result.is_failure
        assert result.value == "value"

    def test_result_fail(self):
        result = Result.fail("error message")
        assert result.is_failure
        assert result.error == "error message"

    def test_exception_hierarchy(self):
        assert issubclass(ValidationError, DomainException)
        assert issubclass(NotFoundError, DomainException)
        assert issubclass(ConflictError, DomainException)
        assert issubclass(AuthorizationError, DomainException)

    def test_domain_event_fields(self):
        agg_id = uuid4()
        event = DomainEvent(event_type="vehicle.registered", aggregate_id=agg_id)
        assert event.aggregate_id == agg_id
        assert event.event_id is not None
        assert event.occurred_at is not None
