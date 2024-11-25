from dataclasses import dataclass
from typing import Callable, Type

from behave import given

@dataclass
class Package:
    alternate_identifier: str

@dataclass
class Event:
    pass

@dataclass
class ResourceStored(Event):
    identifier: str
    alternate_identifier: str

@dataclass
class Resource:
    identifier: str
    alternate_identifier: str

# subclass Repository Gateway some day?
class FakeRepositoryGateway():

    def __init__(self):
        self.store = dict()

    def has_object(self, object_id: str):
        return object_id in self.store

class FakeMessageBus():

    def __init__(self, handlers: dict[Type[Event], list[Callable]]):
        self.handlers = handlers

    def handle(self, event: Event):
        for handler in self.handlers[type(event)]:
            handler(event)

@given(u'a package containing the scanned pages, OCR, and metadata')
def step_impl(context) -> None:
    context.package = Package(alternate_identifier="abc123youandme")

    def resource_stored(event: ResourceStored):
        context.stored_event = event

    handlers: dict[Type[Event], list[Callable]] = {
        ResourceStored: [resource_stored]
    }
    context.message_bus = FakeMessageBus(handlers=handlers)
    context.repository_gateway = FakeRepositoryGateway()

@when(u'the Collection Manager places the packaged resource in the incoming location')
def step_impl(context):
    # Roger will try to fill this out starting with comments
    raise NotImplementedError()

@then(u'the Collection Manager can see that it was preserved')
def step_impl(context):
    event = context.stored_event
    assert event.alternate_identifier == "abc123youandme"
    assert context.repository_gateway.has_object(event.identifier)
