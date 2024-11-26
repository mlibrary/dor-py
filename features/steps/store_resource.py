from dataclasses import dataclass, field
import uuid
from typing import Any, Callable, Type

from behave import given, when, then

@dataclass
class Package:
    alternate_identifier: str

@dataclass
class Item:
    identifier: str

@dataclass
class Resource:
    identifier: str
    alternate_identifier: str

    # blah blah mockyrie leakage
    # @property
    # def internal_resource(self):
    #     return self.__class__.__name__

@dataclass
class Monograph(Resource):
    member_identifiers: list[str] = field(default_factory=list)

@dataclass
class TechnicalMetadata:
    id: str
    file_identifier: str
    mimetype: str

@dataclass
class FileMetadata:
    id: str
    file_identifier: str
    mimetype: str
    technical_metadata: TechnicalMetadata
    use: str

@dataclass
class Asset(Resource):
    file_metadata: list[FileMetadata] = field(default_factory=list)

@dataclass
class Event:
    pass

@dataclass
class PackageSubmitted(Event):
    package_identifier: str

@dataclass
class PackageReceived(Event):
    package_identifier: str
    tracking_identifier: str

@dataclass
class PackageVerified(Event):
    package_identifier: str
    tracking_identifier: str

@dataclass
class ItemUnpacked(Event):
    identifier: str
    alternate_identifier: str
    resources: list[Any]
    tracking_identifier: str

@dataclass
class ItemStored(Event):
    identifier: str
    alternate_identifier: str
    tracking_identifier: str

# subclass Repository Gateway some day?
class FakeRepositoryGateway():

    def __init__(self):
        self.store = dict()

    def has_object(self, object_id: str):
        return object_id in self.store

class FakeUnitOfWork:

    def __init__(self) -> None:
        self.gateway = FakeRepositoryGateway()
        self.events: list[Event] = []

    def add_event(self, event: Event):
        self.events.append(event)

    def pop_event(self) -> Event:
        return self.events.pop(0)

class FakeMessageBus():

    def __init__(self, handlers: dict[Type[Event], list[Callable]]):
        self.handlers = handlers

    def handle(self, event: Event):
        for handler in self.handlers[type(event)]:
            handler(event)

class BagAdapter():

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier

    def is_valid(self) -> bool:
        return True

def receive_package(event: PackageReceived, uow: FakeUnitOfWork) -> None:
    event = PackageReceived(
        package_identifier=event.package_identifier,
        tracking_identifier='ainthtatpeculiar'
    )
    uow.add_event(event)
    # context.identifier = 'blameitontheboogie'

def verify_package(event: PackageReceived, uow: FakeUnitOfWork) -> None:
    bag = BagAdapter(event.package_identifier)
    is_valid =  bag.is_valid()

    if is_valid:
        uow.add_event(PackageVerified(
            package_identifier=event.package_identifier,
            tracking_identifier=event.tracking_identifier
        ))
    else:
        raise Exception()

def unpack_item(event: PackageVerified, uow: FakeUnitOfWork) -> None:
    identifier = str(uuid.uuid4())
    unpacked_event = ItemUnpacked(
        identifier=identifier,
        alternate_identifier="abc123youandme",
        tracking_identifier=event.tracking_identifier,
        resources=[
            Monograph(
                identifier=identifier,
                alternate_identifier="abc123youandme",
                member_identifiers=["asset001", "asset002"]
            ),
            Asset(
                identifier="asset001",
                alternate_identifier="001",
                file_metadata=[
                    FileMetadata(
                        id="_0001.source",
                        file_identifier="0001.source.jpg",
                        mimetype="image/jpeg",
                        technical_metadata=TechnicalMetadata(
                            id="_0001.source.mix",
                            file_identifier="0001.source.xml",
                            mimetype="text/xml",
                        ),
                        use="preservation",
                    )
                ]
            )
        ]
    )
    uow.add_event(unpacked_event)

def store_item(event: PackageVerified, uow: FakeUnitOfWork) -> None:
    pass
    # for path in event.paths:
    #     context.repository_gateway.add(context.identifier, path)

@given(u'a package containing the scanned pages, OCR, and metadata')
def step_impl(context) -> None:
    context.package = Package(alternate_identifier="abc123youandme")
    context.uow = FakeUnitOfWork()
    context.stored_event = None

    def stored_callback(event: ItemStored, uow: FakeUnitOfWork) -> None:
        context.stored_event = event

    handlers: dict[Type[Event], list[Callable]] = {
        PackageSubmitted: [lambda event: receive_package(event, context.uow)],
        PackageReceived: [lambda event: verify_package(event, context.uow)],
        PackageVerified: [lambda event: unpack_item(event, context.uow)],
        ItemUnpacked: [lambda event: store_item(event, context.uow)],
        ItemStored: [lambda event: stored_callback(event, context.uow)]
    }
    context.message_bus = FakeMessageBus(handlers=handlers)

@when(u'the Collection Manager places the packaged resource in the incoming location')
def step_impl(context):
    event = PackageSubmitted(package_identifier='2468')
    context.message_bus.handle(event)

@then(u'the Collection Manager can see that it was preserved.')
def step_impl(context):
    event = context.stored_event
    assert event.alternate_identifier == "abc123youandme"
    assert context.uow.gateway.has_object(event.identifier)
