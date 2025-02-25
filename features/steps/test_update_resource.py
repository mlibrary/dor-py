"""Update Resource feature tests."""
import uuid
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Callable, Type 

import pytest
from pytest_bdd import scenario, given, when, then

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dor.adapters.bag_adapter import BagAdapter
from dor.adapters.sqlalchemy import Base, _custom_json_serializer
from dor.config import config
from dor.domain.events import (
    Event,
    PackageReceived,
    PackageStored,
    PackageSubmitted,
    PackageVerified,
    PackageUnpacked,
    RevisionCataloged,
    WorkspaceCleaned
)
from dor.domain.models import WorkflowEventType
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.package_resource_provider import PackageResourceProvider
from dor.providers.translocator import Translocator, Workspace
from dor.service_layer.handlers.catalog_revision import catalog_revision
from dor.service_layer.handlers.receive_package import receive_package
from dor.service_layer.handlers.record_workflow_event import record_workflow_event
from dor.service_layer.handlers.store_files import store_files
from dor.service_layer.handlers.unpack_package import unpack_package
from dor.service_layer.handlers.verify_package import verify_package
from dor.service_layer.handlers.cleanup_workspace import cleanup_workspace
from dor.service_layer.message_bus.memory_message_bus import MemoryMessageBus
from dor.service_layer.unit_of_work import AbstractUnitOfWork, SqlalchemyUnitOfWork
from gateway.ocfl_repository_gateway import OcflRepositoryGateway

@dataclass
class PathData:
    scratch: Path
    storage: Path
    workspaces: Path
    inbox: Path

@pytest.fixture
def path_data() -> PathData:
    scratch = Path("./features/scratch-update")

    return PathData(
        scratch=scratch,
        inbox=Path("./features/fixtures/inbox"),
        workspaces=scratch / "workspaces",
        storage=scratch / "storage"
    )

@pytest.fixture
def unit_of_work(path_data: PathData) -> AbstractUnitOfWork:
    engine = create_engine(
        config.get_test_database_engine_url(), json_serializer=_custom_json_serializer
    )
    session_factory = sessionmaker(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    gateway = OcflRepositoryGateway(storage_path=path_data.storage)

    return SqlalchemyUnitOfWork(gateway=gateway, session_factory=session_factory)

@pytest.fixture
def message_bus(path_data: PathData, unit_of_work: AbstractUnitOfWork) -> MemoryMessageBus:
    value = '55ce2f63-c11a-4fac-b3a9-160305b1a0c4'
    translocator = Translocator(
        inbox_path=path_data.inbox,
        workspaces_path=path_data.workspaces,
        minter = lambda: value,
        file_provider=FilesystemFileProvider()
    )

    handlers: dict[Type[Event], list[Callable]] = {
        PackageSubmitted: [
            lambda event: record_workflow_event(event, unit_of_work),
            lambda event: receive_package(event, unit_of_work, translocator)
        ],
        PackageReceived: [
            lambda event: record_workflow_event(event, unit_of_work),
            lambda event: verify_package(event, unit_of_work, BagAdapter, Workspace, FilesystemFileProvider())
        ],
        PackageVerified: [
            lambda event: record_workflow_event(event, unit_of_work),
            lambda event: unpack_package(
                event,
                unit_of_work,
                BagAdapter,
                PackageResourceProvider,
                Workspace,
                FilesystemFileProvider(),
            )
        ],
        PackageUnpacked: [
            lambda event: record_workflow_event(event, unit_of_work),
            lambda event: store_files(event, unit_of_work, Workspace)
        ],
        PackageStored: [
            lambda event: record_workflow_event(event, unit_of_work),
            lambda event: catalog_revision(event, unit_of_work)
        ],
        RevisionCataloged: [
            lambda event: record_workflow_event(event, unit_of_work),
            lambda event: cleanup_workspace(event, unit_of_work, Workspace, FilesystemFileProvider())
        ],
        WorkspaceCleaned: [
            lambda event: record_workflow_event(event, unit_of_work)
        ]
    }
    message_bus = MemoryMessageBus(handlers)
    return message_bus


scenario = partial(scenario, '../update_resource.feature')

@scenario('Updating a resource for immediate release')
def test_updating_a_resource_for_immediate_release():
    """Updating a resource for immediate release."""


@given('a package containing all the scanned pages, OCR, and metadata')
def _(path_data: PathData, unit_of_work: AbstractUnitOfWork, message_bus: MemoryMessageBus):
    """a package containing all the scanned pages, OCR, and metadata."""
    file_provider = FilesystemFileProvider()
    file_provider.delete_dir_and_contents(path=path_data.scratch)
    file_provider.create_directory(path_data.scratch)
    file_provider.create_directory(path_data.storage)
    file_provider.create_directory(path_data.workspaces)

    unit_of_work.gateway.create_repository()

    submission_id = "xyzzy-00000000-0000-0000-0000-000000000001-v1"
    tracking_identifier = str(uuid.uuid4())

    event = PackageSubmitted(
        package_identifier=submission_id,
        tracking_identifier=tracking_identifier,
        update_flag=False,
    )
    message_bus.handle(event, unit_of_work)


@when('the Collection Manager places the packaged resource in the incoming location')
def _(message_bus: MemoryMessageBus, unit_of_work: AbstractUnitOfWork):
    """the Collection Manager places the packaged resource in the incoming location."""
    submission_id = "xyzzy-00000000-0000-0000-0000-000000000001-v1"
    tracking_identifier = str(uuid.uuid4())

    event = PackageSubmitted(
        package_identifier=submission_id,
        tracking_identifier=tracking_identifier,
        update_flag=True,
    )
    message_bus.handle(event, unit_of_work)
    return tracking_identifier

@then('the Collection Manager can see that it was revised.')
def _(unit_of_work: AbstractUnitOfWork, tracking_identifier: str):
    """the Collection Manager can see that it was revised.."""
    expected_identifier = "00000000-0000-0000-0000-000000000001"
    assert unit_of_work.gateway.has_object(expected_identifier)

    with unit_of_work:
        revision = unit_of_work.catalog.get(expected_identifier)
        assert revision is not None

        workflow_events = unit_of_work.event_store.get_all_for_tracking_identifier(tracking_identifier)
        assert len(workflow_events) != 0
        assert workflow_events[0].event_type == WorkflowEventType.REVISION_CATALOGED