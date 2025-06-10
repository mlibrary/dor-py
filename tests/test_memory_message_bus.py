import pytest
from dataclasses import dataclass
from typing import Callable

from dor.domain.commands import Command
from dor.domain.events import Event
from dor.service_layer.message_bus.memory_message_bus import MemoryMessageBus, NoHandlerForEventError, CommandHandlerAlreadyRegistered
from dor.service_layer.unit_of_work import AbstractUnitOfWork, UnitOfWork
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

# Ping and Pong are a command/event pair to echo a value over the bus.
# This simulates a command with a side effect that emits a related domain event.
@dataclass
class Ping(Command):
    value: str

@dataclass
class Pong(Event):
    value: str

def echo(cmd, uow):
    uow.add_event(Pong(cmd.value))

class EventSpy:
    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self.value = None

    def record(self, event):
        self.value = event.value

def test_message_bus_commands_can_emit_events() -> None:
    uow = UnitOfWork(FakeRepositoryGateway())
    spy = EventSpy(uow)
    event_handlers: dict[type[Event], list[Callable]] = {
        Pong: [spy.record]
    }
    command_handlers: dict[type[Command], Callable] = {
        Ping: lambda event: echo(event, uow)
    }
    message_bus = MemoryMessageBus(event_handlers, command_handlers, uow=uow)

    message_bus.handle(Ping("hello"))

    assert spy.value == "hello"


def test_message_bus_can_handle_cascading_events() -> None:
    events_seen: list[Event] = []

    def respond_to_a(event: EventA, uow: UnitOfWork):
        events_seen.append(event)
        uow.add_event(EventB(id="2"))

    def respond_to_b(event: EventB, uow: UnitOfWork):
        events_seen.append(event)

    uow = UnitOfWork(FakeRepositoryGateway())
    event_handlers: dict[type[Event], list[Callable]] = {
        EventA: [lambda event: respond_to_a(event, uow)],
        EventB: [lambda event: respond_to_b(event, uow)],
    }
    message_bus = MemoryMessageBus(event_handlers, {}, uow=uow)
    
    message_bus.handle(EventA(id="1"))

    assert [EventA(id="1"), EventB(id="2")] == events_seen

def test_message_bus_with_single_event() -> None:
    events_seen: list[Event] = []

    def respond_to_a(event: EventA, uow: UnitOfWork):
        events_seen.append(event)

    uow = UnitOfWork(FakeRepositoryGateway())
    event_handlers: dict[type[Event], list[Callable]] = {
        EventA: [lambda event: respond_to_a(event, uow)]
    }
    message_bus = MemoryMessageBus(event_handlers, {}, uow=uow)
    
    message_bus.handle(EventA(id="1"))

    assert events_seen == [EventA(id="1")]

def test_message_bus_throws_error_for_event_with_no_handlers() -> None:
    uow = UnitOfWork(FakeRepositoryGateway())
    event_handlers: dict[type[Event], list[Callable]] = {}
    message_bus = MemoryMessageBus(event_handlers, {}, uow=uow)

    with pytest.raises(NoHandlerForEventError):
        message_bus.handle(EventA(id="1"))

def test_message_bus_can_handle_multiple_handlers_for_same_event() -> None:
    events_seen: list[Event] = []

    def first_handler(event: EventA, uow: UnitOfWork):
        events_seen.append(f"first: {event.id}")

    def second_handler(event: EventA, uow: UnitOfWork):
        events_seen.append(f"second: {event.id}")

    uow = UnitOfWork(FakeRepositoryGateway())
    event_handlers: dict[type[Event], list[Callable]] = {
            EventA: [lambda event: first_handler(event, uow),
                     lambda event: second_handler(event, uow)]
    }
    message_bus = MemoryMessageBus(event_handlers, {}, uow=uow)

    message_bus.handle(EventA(id="1"))

    assert events_seen == ["first: 1", "second: 1"]          

def test_events_registered_at_runtime_are_handled() -> None:
    events_seen: list[str] = []

    def handle(event: EventA, uow: UnitOfWork):
        events_seen.append(event.id)

    uow = UnitOfWork(FakeRepositoryGateway())
    message_bus = MemoryMessageBus({}, {}, uow=uow)
    message_bus.register_event_handler(EventA, lambda event: handle(event, uow))

    message_bus.handle(EventA("dynamic"))

    assert events_seen == ["dynamic"]

def test_commands_registered_at_runtime_are_handled() -> None:
    uow = UnitOfWork(FakeRepositoryGateway())
    spy = EventSpy(uow)
    message_bus = MemoryMessageBus({Pong: [spy.record]}, {}, uow=uow)
    message_bus.register_command_handler(Ping, lambda event: echo(event, uow))

    result = message_bus.handle(Ping("dynamic"))

    assert spy.value == "dynamic"

def test_commands_support_only_one_handler() -> None:
    uow = UnitOfWork(FakeRepositoryGateway())
    message_bus = MemoryMessageBus({}, {}, uow=uow)
    message_bus.register_command_handler(Ping, lambda x: x)

    with pytest.raises(CommandHandlerAlreadyRegistered, match="'Ping'"):
        message_bus.register_command_handler(Ping, lambda x: x)
