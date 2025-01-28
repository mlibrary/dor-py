import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, select, Uuid
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from dor.adapters.sqlalchemy import Base
from dor.domain import models


class EventStore(ABC):

    @abstractmethod
    def add(self, event: models.WorkflowEvent):
        raise NotImplementedError

    @abstractmethod
    def get_all_by_tracking_identifier(self, tracking_identifier: str) -> list[models.WorkflowEvent]:
        raise NotImplementedError


class MemoryEventStore(EventStore):

    def __init__(self):
        self.events: list[models.WorkflowEvent] = []

    def add(self, event: models.WorkflowEvent) -> None:
        self.events.append(event)

    def get_all_by_tracking_identifier(self, tracking_identifier: str) -> list[models.WorkflowEvent]:
        return [
            event for event in self.events
            if event.tracking_identifier == tracking_identifier
        ]


class WorkflowEvent(Base):
    __tablename__ = "workflow_event"

    identifier: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    package_identifier: Mapped[str] = mapped_column(String(30))
    tracking_identifier: Mapped[str] = mapped_column(String(30))
    event_type: Mapped[str] = mapped_column(String(30))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    message: Mapped[Optional[str]] = mapped_column(String(1000))


class SqlalchemyEventStore(EventStore):

    def __init__(self, session):
        self.session = session

    def add(self, event: models.WorkflowEvent) -> None:
        stored_event = WorkflowEvent(
            identifier=event.identifier,
            package_identifier=event.package_identifier,
            tracking_identifier=event.tracking_identifier,
            event_type=event.event_type.value,
            timestamp=event.timestamp,
            message=event.message
        )
        self.session.add(stored_event)

    def get_all_by_tracking_identifier(self, tracking_identifier: str) -> list[models.WorkflowEvent]:
        statement = select(WorkflowEvent).where(
            WorkflowEvent.tracking_identifier == tracking_identifier
        )
        results = self.session.scalars(statement).all()
        events = []
        for result in results:
            events.append(
                models.WorkflowEvent(
                    identifier=result.identifier,
                    package_identifier=result.package_identifier,
                    tracking_identifier=result.tracking_identifier,
                    event_type=models.WorkflowEventType(result.event_type),
                    timestamp=result.timestamp,
                    message=result.message
                )
            )
        return events
