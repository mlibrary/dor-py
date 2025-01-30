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
        workflow_events = [
            event for event in self.events
            if event.tracking_identifier == tracking_identifier
        ]
        return sorted(workflow_events, key=lambda x: x.timestamp, reverse=True)


class WorkflowEvent(Base):
    __tablename__ = "workflow_event"

    identifier: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    package_identifier: Mapped[str] = mapped_column(String(50))
    tracking_identifier: Mapped[str] = mapped_column(String(50))
    event_type: Mapped[str] = mapped_column(String(50))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    message: Mapped[Optional[str]] = mapped_column(String(1000))


class SqlalchemyEventStore(EventStore):

    def __init__(self, session):
        self.session = session

    @staticmethod
    def _convert_domain_to_orm(event: models.WorkflowEvent) -> WorkflowEvent:
        return WorkflowEvent(
            identifier=event.identifier,
            package_identifier=event.package_identifier,
            tracking_identifier=event.tracking_identifier,
            event_type=event.event_type.value,
            timestamp=event.timestamp,
            message=event.message
        )

    @staticmethod
    def _convert_orm_to_domain(event: WorkflowEvent) -> models.WorkflowEvent:
        return models.WorkflowEvent(
            identifier=event.identifier,
            package_identifier=event.package_identifier,
            tracking_identifier=event.tracking_identifier,
            event_type=models.WorkflowEventType(event.event_type),
            timestamp=event.timestamp,
            message=event.message
        )

    def add(self, event: models.WorkflowEvent) -> None:
        stored_event = self._convert_domain_to_orm(event)
        self.session.add(stored_event)

    def get_all_by_tracking_identifier(self, tracking_identifier: str) -> list[models.WorkflowEvent]:
        statement = select(WorkflowEvent).where(
            WorkflowEvent.tracking_identifier == tracking_identifier
        ).order_by(WorkflowEvent.timestamp.desc())

        results = self.session.scalars(statement).all()
        events = []
        for result in results:
            events.append(self._convert_orm_to_domain(result))
        return events
