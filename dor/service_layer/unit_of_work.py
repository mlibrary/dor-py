from abc import ABC, abstractmethod

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dor.adapters.catalog import Catalog, MemoryCatalog, SqlalchemyCatalog
from dor.adapters.event_store import EventStore, MemoryEventStore, SqlalchemyEventStore
from dor.adapters.sqlalchemy import _custom_json_serializer
from dor.config import config
from dor.domain.events import Event
from gateway.repository_gateway import RepositoryGateway


class AbstractUnitOfWork(ABC):
    catalog: Catalog
    event_store: EventStore
    gateway: RepositoryGateway

    @abstractmethod
    def __enter__(self):
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, *args):
        raise NotImplementedError

    @abstractmethod
    def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError

    def add_event(self, event: Event):
        raise NotImplementedError

    def pop_event(self) -> Event | None:
        raise NotImplementedError


class UnitOfWork(AbstractUnitOfWork):

    def __init__(self, gateway: RepositoryGateway) -> None:
        self.gateway = gateway
        self.events: list[Event] = []
        self.catalog = MemoryCatalog()
        self.event_store = MemoryEventStore()

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self.committed = True

    def rollback(self):
        pass

    def add_event(self, event: Event):
        self.events.append(event)

    def pop_event(self) -> Event | None:
        if len(self.events) > 0:
            return self.events.pop(0)
        return None


DEFAULT_SESSION_FACTORY = sessionmaker(bind=create_engine(
    config.get_database_engine_url(), json_serializer=_custom_json_serializer
))


class SqlalchemyUnitOfWork(AbstractUnitOfWork):

    def __init__(self, gateway: RepositoryGateway, session_factory=DEFAULT_SESSION_FACTORY) -> None:
        self.session_factory = session_factory
        self.gateway: RepositoryGateway = gateway
        self.events: list[Event] = []

    def __enter__(self):
        self.session = self.session_factory()
        self.catalog = SqlalchemyCatalog(self.session)
        self.event_store = SqlalchemyEventStore(self.session)

    def __exit__(self, *args):
        self.rollback()
        self.session.close()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()

    def add_event(self, event: Event):
        self.events.append(event)

    def pop_event(self) -> Event | None:
        if len(self.events) > 0:
            return self.events.pop(0)
        return None
