from dataclasses import dataclass
from typing import Callable

from dor.domain.events import Event
from dor.service_layer.message_bus.memory_message_bus import MemoryMessageBus
from dor.service_layer.unit_of_work import UnitOfWork
from gateway.fake_repository_gateway import FakeRepositoryGateway


@dataclass
class EventA(Event):
    id: str


@dataclass
class EventB(Event):
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

# More tests coming...
