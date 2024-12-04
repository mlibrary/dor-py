import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Set, Type
from dor.domain.events import (
    Event,
    PackageReceived,
    PackageSubmitted,
    PackageVerified,
    ItemStored,
    ItemUnpacked
)
from dor.domain.models import Coordinator, VersionInfo

from behave import given, when, then

@dataclass
class Item:
    identifier: str

# Resource

@dataclass
class Resource:
    identifier: str | None

    # blah blah mockyrie leakage
    # @property
    # def internal_resource(self):
    #     return self.__class__.__name__

@dataclass
class Monograph(Resource):
    alternate_identifier: str
    member_identifiers: list[str] = field(default_factory=list)

    def get_entries(self) -> list[Path]:
        return []

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

    def get_entries(self) -> list[Path]:
        entries = []
        for file_metadata in self.file_metadata:
            entries.append(Path(file_metadata.file_identifier))
            entries.append(Path(file_metadata.technical_metadata.file_identifier))
        return entries

# Gateway

@dataclass
class FakePackage:
    package_identifier: str
    entries: list[Path]

    def get_paths(self) -> list[Path]:
        return self.entries

@dataclass
class RepositoryObject:
    staged_files: Set[str]
    files: Set[str]

# subclass Repository Gateway some day?
class FakeRepositoryGateway():

    def __init__(self) -> None:
        self.store: dict[str, RepositoryObject] = dict()

    def create_repository(self):
        pass

    def has_object(self, object_id: str):
        return object_id in self.store and len(self.store[object_id].files) > 0

    def create_staged_object(self, id: str) -> None:
        self.store[id] = RepositoryObject(staged_files=set(), files=set())

    def stage_object_files(self, id: str, source_package: FakePackage) -> None:
        file_paths = set(source_package.get_paths())
        if id not in self.store:
            raise Exception()
        self.store[id].staged_files = self.store[id].staged_files.union(file_paths)

    def commit_object_changes(
        self,
        id: str,
        coordinator: Coordinator,
        message: str
    ) -> None:
        if id not in self.store:
            raise Exception()
        self.store[id].files = self.store[id].files.union(self.store[id].staged_files)
        self.store[id].staged_files = set()

class FakeUnitOfWork:

    def __init__(self) -> None:
        self.gateway = FakeRepositoryGateway()
        self.gateway.create_repository()

        self.events: list[Event] = []

    def add_event(self, event: Event):
        self.events.append(event)

    def pop_event(self) -> Event | None:
        if len(self.events) > 0:
            return self.events.pop(0)
        return None

class FakeMessageBus():

    def __init__(self, handlers: dict[Type[Event], list[Callable]]):
        self.handlers = handlers

    def handle(self, event: Event, uow: FakeUnitOfWork):
        queue = [event]
        while queue:
            next_event = queue.pop(0)
            for handler in self.handlers[type(next_event)]:
                handler(next_event)
            another_event = uow.pop_event()
            if another_event:
                queue.append(another_event)

class BagAdapter():

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier

    def is_valid(self) -> bool:
        return True

class FakeMETSProvider:

    def __init__(self, path: Path):
        self.path = path

    def get_resources(self):
        return [
            Monograph(
                identifier="abc123youandme",
                alternate_identifier="jackson.abc123youandme",
                member_identifiers=["asset001", "asset002"]
            ),
            Asset(
                identifier="001",
                file_metadata=[
                    FileMetadata(
                        id="_0001.source",
                        file_identifier="data/0001.source.jpg",
                        mimetype="image/jpeg",
                        technical_metadata=TechnicalMetadata(
                            id="_0001.source.mix",
                            file_identifier="metadata/0001.source.xml",
                            mimetype="text/xml",
                        ),
                        use="preservation",
                    )
                ]
            )
        ]


# Handlers

def receive_package(event: PackageReceived, uow: FakeUnitOfWork) -> None:
    # some component needed that fakes moving the package to the processing directory
    event = PackageReceived(
        package_identifier=event.package_identifier,
        tracking_identifier='aintthatpeculiar'
    )
    uow.add_event(event)
    # context.identifier = 'blameitontheboogie'

def verify_package(event: PackageReceived, uow: FakeUnitOfWork) -> None:
    bag = BagAdapter(event.package_identifier)
    is_valid = bag.is_valid()

    if is_valid:
        uow.add_event(PackageVerified(
            package_identifier=event.package_identifier,
            tracking_identifier=event.tracking_identifier
        ))
    else:
        raise Exception()

def unpack_item(event: PackageVerified, uow: FakeUnitOfWork) -> None:
    resources = FakeMETSProvider(Path(event.package_identifier)).get_resources()

    unpacked_event = ItemUnpacked(
        identifier="abc123youandme",
        tracking_identifier=event.tracking_identifier,
        package_identifier=event.package_identifier,
        resources=resources,
        version_info=VersionInfo(
            coordinator=Coordinator("jermaine", "jermaine@jackson5.com"),
            message="Just call my name, I'll be there"
        )
    )
    uow.add_event(unpacked_event)

def store_item(event: ItemUnpacked, uow: FakeUnitOfWork) -> None:
    entries = []
    for resource in event.resources:
        entries.extend(resource.get_entries())

    package = FakePackage(package_identifier=event.package_identifier, entries=entries)

    uow.gateway.create_staged_object(id=event.identifier)
    uow.gateway.stage_object_files(
        id=event.identifier, 
        source_package=package,
    )
    uow.gateway.commit_object_changes(
        id=event.identifier,
        coordinator=event.version_info.coordinator,
        message=event.version_info.message
    )

    stored_event = ItemStored(
        identifier=event.identifier,
        tracking_identifier=event.tracking_identifier
    )
    uow.add_event(stored_event)

# Test

@given(u'a package containing the scanned pages, OCR, and metadata')
def step_impl(context) -> None:
    context.uow = FakeUnitOfWork()

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
    context.message_bus.handle(event, context.uow)

@then(u'the Collection Manager can see that it was preserved.')
def step_impl(context):
    event = context.stored_event
    assert event.identifier == "abc123youandme"
    assert context.uow.gateway.has_object(event.identifier)
