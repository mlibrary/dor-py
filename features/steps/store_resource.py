from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Type
from dor.domain.events import (
    Event,
    PackageReceived,
    PackageSubmitted,
    PackageVerified,
    ItemStored,
    ItemUnpacked
)
from dor.domain.models import Coordinator, VersionInfo, Workspace

from behave import given, when, then
from dor.service_layer.message_bus.memory_message_bus import MemoryMessageBus
from dor.service_layer.unit_of_work import UnitOfWork
from gateway.fake_repository_gateway import FakePackage, FakeRepositoryGateway
from dor.service_layer.handlers.receive_package import receive_package, Translocator

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

class FakeBagReader():

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier

    def is_valid(self) -> bool:
        return True
    
    @property
    def dor_info(self) -> dict:
        return {}

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



def verify_package(event: PackageReceived, uow: UnitOfWork, bag_reader_class: type) -> None:
    workspace = Workspace.find(event.workspace_identifier)

    bag_reader = bag_reader_class(workspace.package_directory)

    is_valid = bag_reader.is_valid()

    if is_valid:
        uow.add_event(PackageVerified(
            package_identifier=event.package_identifier,
            tracking_identifier=event.tracking_identifier
        ))
    else:
        raise Exception()

def unpack_item(event: PackageVerified, uow: UnitOfWork) -> None:
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

def store_item(event: ItemUnpacked, uow: UnitOfWork) -> None:
    entries = []
    for resource in event.resources:
        entries.extend(resource.get_entries())

    package = FakePackage(root_path=Path("/"), entries=entries)

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
    context.uow = UnitOfWork(gateway=FakeRepositoryGateway())
    context.translocator = Translocator()

    def stored_callback(event: ItemStored, uow: UnitOfWork) -> None:
        context.stored_event = event

    handlers: dict[Type[Event], list[Callable]] = {
        PackageSubmitted: [lambda event: receive_package(event, context.uow, context.translocator)],
        PackageReceived: [lambda event: verify_package(event, context.uow, FakeBagReader)],
        PackageVerified: [lambda event: unpack_item(event, context.uow)],
        ItemUnpacked: [lambda event: store_item(event, context.uow)],
        ItemStored: [lambda event: stored_callback(event, context.uow)]
    }
    context.message_bus = MemoryMessageBus(handlers)

@when(u'the Collection Manager places the packaged resource in the incoming location')
def step_impl(context):
    event = PackageSubmitted(package_identifier='2468')
    context.message_bus.handle(event, context.uow)

@then(u'the Collection Manager can see that it was preserved.')
def step_impl(context):
    event = context.stored_event
    assert event.identifier == "abc123youandme"
    assert context.uow.gateway.has_object(event.identifier)
