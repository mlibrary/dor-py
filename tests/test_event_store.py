import uuid
from datetime import datetime, timedelta, UTC

import pytest
import sqlalchemy

from dor.adapters.event_store import MemoryEventStore, SqlalchemyEventStore
from dor.domain.models import WorkflowEvent, WorkflowEventType


@pytest.fixture
def workflow_event() -> WorkflowEvent:
    return WorkflowEvent(
        identifier=uuid.uuid4(),
        package_identifier="xyzzy-0001-v1",
        tracking_identifier="some-tracking-id",
        event_type=WorkflowEventType.PACKAGE_STORED,
        timestamp=datetime.now(tz=UTC),
        message=None
    )

@pytest.fixture
def workflow_events(workflow_event) -> list[WorkflowEvent]:
    return [
        workflow_event,
        WorkflowEvent(
            identifier=uuid.uuid4(),
            package_identifier="xyzzy-0001-v1",
            tracking_identifier="some-tracking-id",
            event_type=WorkflowEventType.VERSION_CATALOGED,
            timestamp=datetime.now(tz=UTC) + timedelta(seconds=20),
            message=None
        )
    ]


def test_memory_event_store_adds_event(workflow_event: WorkflowEvent):
    event_store = MemoryEventStore()
    event_store.add(workflow_event)

    assert event_store.events == [workflow_event]


def test_memory_event_store_gets_events_by_tracking_identifier(workflow_events: list[WorkflowEvent]):
    event_store = MemoryEventStore()
    for workflow_event in workflow_events:
        event_store.add(workflow_event)

    events = event_store.get_all_for_tracking_identifier("some-tracking-id")
    assert events == [workflow_events[1], workflow_events[0]]


@pytest.mark.usefixtures("db_session")
def test_sqlalchemy_event_store_adds_event(db_session, workflow_event: WorkflowEvent):
    event_store = SqlalchemyEventStore(db_session)
    with db_session.begin():
        event_store.add(workflow_event)
        db_session.commit()

    rows = list(
        db_session.execute(sqlalchemy.text("""
            select *
            from workflow_event
            where identifier = :identifier
        """), { "identifier": workflow_event.identifier })
    )
    assert len(rows) == 1
    assert rows[0].identifier == workflow_event.identifier


@pytest.mark.usefixtures("db_session")
def test_sqlalchemy_event_store_gets_events_by_tracking_identifier(db_session, workflow_events: list[WorkflowEvent]):
    event_store = SqlalchemyEventStore(db_session)
    with db_session.begin():
        for workflow_event in workflow_events:
            event_store.add(workflow_event)
        db_session.commit()

    events = event_store.get_all_for_tracking_identifier(workflow_event.tracking_identifier)
    assert events == [workflow_events[1], workflow_events[0]]
