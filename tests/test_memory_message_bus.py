import pytest
from dataclasses import dataclass
from typing import Callable

from dor.domain.commands import Command
from dor.domain.events import Event
from dor.service_layer.message_bus.memory_message_bus import MemoryMessageBus, NoHandlerForEventError, CommandHandlerAlreadyRegistered
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

@dataclass
class Echo(Command):
    value: str

def echo(cmd, uow):
    return cmd.value


def test_message_bus_command_returns_result() -> None:
    uow = UnitOfWork(FakeRepositoryGateway())
    command_handlers: dict[type[Command], Callable] = {
        Echo: echo
    }
    message_bus = MemoryMessageBus(
        event_handlers={},
        command_handlers=command_handlers
    )

    value = message_bus.handle(Echo("hello"), uow)

    assert value == "hello"


def test_message_bus_can_handle_cascading_events() -> None:
    events_seen: list[Event] = []

    def respond_to_a(event: EventA, uow: UnitOfWork):
        events_seen.append(event)
        uow.add_event(EventB(id="2"))

    def respond_to_b(event: EventB, uow: UnitOfWork):
        events_seen.append(event)

    uow = UnitOfWork(FakeRepositoryGateway())
    event_handlers: dict[type[Event], list[Callable]] = {
        EventA: [respond_to_a],
        EventB: [respond_to_b],
    }
    message_bus = MemoryMessageBus(event_handlers)
    
    message_bus.handle(EventA(id="1"), uow)

    assert [EventA(id="1"), EventB(id="2")] == events_seen

def test_message_bus_with_single_event() -> None:
    events_seen: list[Event] = []

    def respond_to_a(event: EventA, uow: UnitOfWork):
        events_seen.append(event)

    uow = UnitOfWork(FakeRepositoryGateway())
    event_handlers: dict[type[Event], list[Callable]] = {
        EventA: [respond_to_a]
    }
    message_bus = MemoryMessageBus(event_handlers)
    
    message_bus.handle(EventA(id="1"), uow)

    assert events_seen == [EventA(id="1")]

def test_message_bus_throws_error_for_event_with_no_handlers() -> None:
    uow = UnitOfWork(FakeRepositoryGateway())
    event_handlers: dict[type[Event], list[Callable]] = {}
    message_bus = MemoryMessageBus(event_handlers)

    with pytest.raises(NoHandlerForEventError):
        message_bus.handle(EventA(id="1"), uow)

def test_message_bus_can_handle_multiple_handlers_for_same_event() -> None:
    events_seen: list[Event] = []

    def first_handler(event: EventA, uow: UnitOfWork):
        events_seen.append(f"first: {event.id}")

    def second_handler(event: EventA, uow: UnitOfWork):
        events_seen.append(f"second: {event.id}")

    uow = UnitOfWork(FakeRepositoryGateway())
    event_handlers: dict[type[Event], list[Callable]] = {
        EventA: [first_handler, second_handler]
    }
    message_bus = MemoryMessageBus(event_handlers)

    message_bus.handle(EventA(id="1"), uow)

    assert events_seen == ["first: 1", "second: 1"]          

def test_events_registered_at_runtime_are_handled() -> None:
    events_seen: list[str] = []

    def handle(event: EventA, uow: UnitOfWork):
        events_seen.append(event.id)

    uow = UnitOfWork(FakeRepositoryGateway())
    message_bus = MemoryMessageBus({}, {})
    message_bus.register_event_handler(EventA, handle)

    message_bus.handle(EventA("dynamic"), uow)

    assert events_seen == ["dynamic"]

def test_commands_registered_at_runtime_are_handled() -> None:
    def handle(command: Echo, uow: UnitOfWork):
        return command.value

    uow = UnitOfWork(FakeRepositoryGateway())
    message_bus = MemoryMessageBus({}, {})
    message_bus.register_command_handler(Echo, handle)

    result = message_bus.handle(Echo("dynamic"), uow)

    assert result == "dynamic"

def test_commands_support_only_one_handler() -> None:
    message_bus = MemoryMessageBus({}, {})
    message_bus.register_command_handler(Echo, lambda x: x)

    with pytest.raises(CommandHandlerAlreadyRegistered, match="'Echo'"):
        message_bus.register_command_handler(Echo, lambda x: x)
