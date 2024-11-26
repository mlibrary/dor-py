from dataclasses import dataclass, field
from typing import Callable, Type

from behave import given

@dataclass
class Package:
    alternate_identifier: str

@dataclass
class Resource:
    identifier: str
    alternate_identifier: str

    # blah blah mockyrie leakage
    @property
    def internal_resource(self):
        return self.__class__.name

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
    technical_metdata: TechnicalMetadata
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
    identifier: str
    alternate_identifier: str
    resources: list[Resource]

@dataclass
class ResourceStored(Event):
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

    def package_submitted(event: PackageSubmitted):
        pass

    def package_received(event: PackageReceived):
        context.identifier = 'blameitontheboogie'
        
    def package_verified(event: PackageVerified):
        for path in event.paths:
            context.repository_gateway.add(context.identifier, path)

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

    event = PackageSubmitted(package_identifier='2468')
    context.message_bus.handle(event)
    # assert?

    event = PackageReceived(package_identifier=event.package_identifier, tracking_identifier='ainthtatpeculiar')
    context.message_bus.handle(event)
    # assert?

    ## --- if you've read the deep dive, should
    ## --- verify and process be combined?
    event = PackageVerified(
        identifier=context.identifier,
        package_identifier=event.package_identifier,
        alternate_identifier="abc123youandme",
        resources=[
            Monograph(
                id=context.identifier,
                alternate_identifier="abc123youandme",
                member_identifiers=["asset001", "asset002"]
            ),
            Asset(
                id="asset001",
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
    context.message_bus.handle(event)
    #### event = PackageProcessed(...)
    #### context.message_bus.handle(event)
    # assert?

    # event = ResourceStored(...)
    # context.message_bus.handle(event)
    # assert?

    # event = ResourceRegistered(...)
    # context.message_bus.handle(event)

    raise NotImplementedError()

@then(u'the Collection Manager can see that it was preserved')
def step_impl(context):
    event = context.stored_event
    assert event.alternate_identifier == "abc123youandme"
    assert context.repository_gateway.has_object(event.identifier)
