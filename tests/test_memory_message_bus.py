import pytest
from dataclasses import dataclass
from typing import Callable

from dor.domain.events import Event
from dor.service_layer.message_bus.memory_message_bus import MemoryMessageBus, NoHandlerForEventError
from dor.service_layer.unit_of_work import UnitOfWork
from gateway.fake_repository_gateway import FakeRepositoryGateway


@dataclass
class EventA(Event):
    id: str


@dataclass
class EventB(Event):
    id: str

@dataclass
class EventC(Event):
    id: str

@dataclass
class OtherEvent(Event):
    id: str

def test_message_bus_can_handle_cascading_events() -> None:
    events_seen: list[Event] = []

    def respond_to_a(event: EventA, uow: UnitOfWork):
        events_seen.append(event)
        uow.add_event(EventB(id="2"))

    def respond_to_b(event: EventB, uow: UnitOfWork):
        events_seen.append(event)

    uow = UnitOfWork(FakeRepositoryGateway())
    handlers: dict[type[Event], list[Callable]] = {
        EventA: [lambda event: respond_to_a(event, uow)],
        EventB: [lambda event: respond_to_b(event, uow)]
    }
    message_bus = MemoryMessageBus(handlers)
    
    message_bus.handle(EventA(id="1"), uow)

    assert [EventA(id="1"), EventB(id="2")] == events_seen

def test_message_bus_with_single_event() -> None:
    events_seen: list[Event] = []

    def respond_to_a(event: EventA, uow: UnitOfWork):
        events_seen.append(event)

    uow = UnitOfWork(FakeRepositoryGateway())
    handlers: dict[type[Event], list[Callable]] = {
        EventA: [lambda event: respond_to_a(event, uow)]
    }
    message_bus = MemoryMessageBus(handlers)
    
    message_bus.handle(EventA(id="1"), uow)

    assert events_seen == [EventA(id="1")]

def test_message_bus_throws_error_for_event_with_no_handlers() -> None:
    uow = UnitOfWork(FakeRepositoryGateway())
    handlers: dict[type[Event], list[Callable]] = {}  
    message_bus = MemoryMessageBus(handlers)

    with pytest.raises(NoHandlerForEventError):
        message_bus.handle(EventA(id="1"), uow)

def test_message_bus_can_handle_multiple_handlers_for_same_event() -> None:
    events_seen: list[Event] = []

    def first_handler(event: EventA, uow: UnitOfWork):
        events_seen.append(f"first: {event.id}")

    def second_handler(event: EventA, uow: UnitOfWork):
        events_seen.append(f"second: {event.id}")

    uow = UnitOfWork(FakeRepositoryGateway())
    handlers: dict[type[Event], list[Callable]] = {
        EventA: [lambda event: first_handler(event, uow), lambda event: second_handler(event, uow)]
    }
    message_bus = MemoryMessageBus(handlers)

    message_bus.handle(EventA(id="1"), uow)

    assert events_seen == ["first: 1", "second: 1"]          

