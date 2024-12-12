from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Type
import uuid

from dor.domain.events import (
    Event,
    PackageReceived,
    PackageStored,
    PackageSubmitted,
    PackageVerified,
    PackageUnpacked
)
from dor.domain.models import FakeWorkspace

from behave import given, when, then
from dor.service_layer.handlers.store_files import store_files
from dor.service_layer.message_bus.memory_message_bus import MemoryMessageBus
from dor.service_layer.unit_of_work import UnitOfWork
from gateway.fake_repository_gateway import FakeRepositoryGateway
from dor.service_layer.handlers.receive_package import receive_package, Translocator
from dor.service_layer.handlers.verify_package import verify_package
from dor.service_layer.handlers.unpack_package import unpack_package
from dor.providers.models import Agent, FileMetadata, FileReference, PackageResource, PreservationEvent, AlternateIdentifier, StructMap, StructMapItem, StructMapType

@dataclass
class Item:
    identifier: str

class FakeBagReader():

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier

    def is_valid(self) -> bool:
        return True
    
    @property
    def dor_info(self) -> dict:
        return {
            'Root-Identifier': "00000000-0000-0000-0000-000000000001"
        }

class FakePackageResourceProvider:

    def __init__(self, path: Path):
        self.path = path

    def get_resources(self):
        return [
            PackageResource(
                id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                type="Monograph",
                alternate_identifier=AlternateIdentifier(id="xyzzy:00000001", type="DLXS"),
                events=[
                    PreservationEvent(
                        identifier="e01727d0-b4d9-47a5-925a-4018f9cac6b8",
                        type="ingest",
                        datetime=datetime(1983, 5, 17, 11, 9, 45, tzinfo=UTC),
                        detail="Girl voice lot another blue nearly.",
                        agent=Agent(
                            address="matthew24@example.net", role="collection manager"
                        ),
                    )
                ],
                metadata_files=[
                    FileMetadata(
                        id="_0193972b-e591-7e28-b8cb-1babed52f606",
                        use="DESCRIPTIVE/COMMON",
                        ref=FileReference(
                            locref="../metadata/00000000-0000-0000-0000-000000000001.common.json",
                            mdtype="DOR:SCHEMA",
                            mimetype="application/json",
                        ),
                    ),
                    FileMetadata(
                        id="_0193972b-e592-7647-8e51-10db514433f7",
                        use="DESCRIPTIVE",
                        ref=FileReference(
                            locref="../metadata/00000000-0000-0000-0000-000000000001.metadata.json",
                            mdtype="DOR:SCHEMA",
                            mimetype="application/json",
                        ),
                    ),
                    FileMetadata(
                        id="RIGHTS1",
                        use="RIGHTS",
                        ref=FileReference(
                            locref="https://creativecommons.org/publicdomain/zero/1.0/",
                            mdtype="OTHER",
                        ),
                    ),
                ],
                struct_maps=[
                    StructMap(
                        id="SM1",
                        type=StructMapType.PHYSICAL,
                        items=[
                            StructMapItem(
                                order=1,
                                type="page",
                                label="Page 1",
                                asset_id="urn:dor:00000000-0000-0000-0000-000000001001",
                            ),
                            StructMapItem(
                                order=2,
                                type="page",
                                label="Page 2",
                                asset_id="urn:dor:00000000-0000-0000-0000-000000001002",
                            ),
                        ],
                    )
                ],
            ),
            PackageResource(
                id=uuid.UUID("00000000-0000-0000-0000-000000001001"),
                type="Asset",
                alternate_identifier=AlternateIdentifier(
                    id="xyzzy:00000001:00000001", type="DLXS"
                ),
                events=[
                    PreservationEvent(
                        identifier="81388465-aefd-4a3d-ba99-a868d062b92e",
                        type="generate access derivative",
                        datetime=datetime(2005, 8, 22, 22, 54, 45, tzinfo=UTC),
                        detail="Method south agree until.",
                        agent=Agent(address="rguzman@example.net", role="image processing"),
                    ),
                    PreservationEvent(
                        identifier="d53540b9-cd23-4e92-9dff-4b28bf050b26",
                        type="extract text",
                        datetime=datetime(2006, 8, 23, 16, 21, 57, tzinfo=UTC),
                        detail="Hear thus part probably that.",
                        agent=Agent(address="kurt16@example.org", role="ocr processing"),
                    ),
                ],
                metadata_files=[
                    FileMetadata(
                        id="_0193972b-e4a4-7985-abe2-f3f1259b78ec",
                        use="TECHNICAL",
                        ref=FileReference(
                            locref="../metadata/00000001.source.jpg.mix.xml",
                            mdtype="NISOIMG",
                        ),
                    ),
                    FileMetadata(
                        id="_0193972b-e4ae-73eb-848d-5f8893b68253",
                        use="TECHNICAL",
                        ref=FileReference(
                            locref="../metadata/00000001.access.jpg.mix.xml",
                            mdtype="NISOIMG",
                        ),
                    ),
                    FileMetadata(
                        id="_0193972b-e572-7107-b69c-e2f4c660a9aa",
                        use="TECHNICAL",
                        ref=FileReference(
                            locref="../metadata/00000001.plaintext.txt.textmd.xml",
                            mdtype="TEXTMD",
                        ),
                    ),
                ],
                data_files=[
                    FileMetadata(
                        id="_be653ff450ae7f3520312a53e56c00bc",
                        mdid="_0193972b-e4a4-7985-abe2-f3f1259b78ec",
                        use="SOURCE",
                        ref=FileReference(
                            locref="../data/00000001.source.jpg",
                            mimetype="image/jpeg",
                        ),
                    ),
                    FileMetadata(
                        id="_7e923d9c33b3859e1327fa53a8e609a1",
                        groupid="_be653ff450ae7f3520312a53e56c00bc",
                        mdid="_0193972b-e4ae-73eb-848d-5f8893b68253",
                        use="ACCESS",
                        ref=FileReference(
                            locref="../data/00000001.access.jpg",
                            mimetype="image/jpeg",
                        ),
                    ),
                    FileMetadata(
                        id="_764ba9761fbc6cbf0462d28d19356148",
                        groupid="_be653ff450ae7f3520312a53e56c00bc",
                        mdid="_0193972b-e572-7107-b69c-e2f4c660a9aa",
                        use="SOURCE",
                        ref=FileReference(
                            locref="../data/00000001.plaintext.txt",
                            mimetype="text/plain",
                        ),
                    ),
                ],
            )
        ]


# - if the workspace is under namespace dor
#   but gateway is outside of it, issues with
#   where code is living.
# - does gateway be moved under dor proper now?

# Test

@given(u'a package containing the scanned pages, OCR, and metadata')
def step_impl(context) -> None:
    context.uow = UnitOfWork(gateway=FakeRepositoryGateway())
    context.translocator = Translocator()

    def stored_callback(event: PackageStored, uow: UnitOfWork) -> None:
        context.stored_event = event

    handlers: dict[Type[Event], list[Callable]] = {
        PackageSubmitted: [lambda event: receive_package(event, context.uow, context.translocator)],
        PackageReceived: [lambda event: verify_package(event, context.uow, FakeBagReader, FakeWorkspace)],
        PackageVerified: [lambda event: unpack_package(
            event, context.uow, FakeBagReader, FakePackageResourceProvider, FakeWorkspace
        )],
        PackageUnpacked: [lambda event: store_files(event, context.uow, FakeWorkspace)],
        PackageStored: [lambda event: stored_callback(event, context.uow)]
    }
    context.message_bus = MemoryMessageBus(handlers)

@when(u'the Collection Manager places the packaged resource in the incoming location')
def step_impl(context):
    event = PackageSubmitted(package_identifier='2468')
    context.message_bus.handle(event, context.uow)

@then(u'the Collection Manager can see that it was preserved.')
def step_impl(context):
    event = context.stored_event
    assert event.identifier == "00000000-0000-0000-0000-000000000001"
    assert context.uow.gateway.has_object(event.identifier)
