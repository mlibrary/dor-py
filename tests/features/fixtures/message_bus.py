import pytest
from typing import Callable, Type

from dor.adapters.bag_adapter import BagAdapter
from dor.config import config
from dor.domain.events import (
    Event,
    PackageReceived,
    PackageStored,
    PackageSubmitted,
    PackageVerified,
    PackageUnpacked,
    RevisionCataloged
)
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.package_resource_provider import PackageResourceProvider
from dor.providers.translocator import Translocator, Workspace
from dor.service_layer.handlers.catalog_revision import catalog_revision
from dor.service_layer.handlers.receive_package import receive_package
from dor.service_layer.handlers.record_workflow_event import record_workflow_event
from dor.service_layer.handlers.store_files import store_files
from dor.service_layer.handlers.unpack_package import unpack_package
from dor.service_layer.handlers.verify_package import verify_package
from dor.service_layer.message_bus.memory_message_bus import MemoryMessageBus
from dor.service_layer.unit_of_work import AbstractUnitOfWork, SqlalchemyUnitOfWork

from utils.minter import minter


@pytest.fixture
def message_bus(unit_of_work: AbstractUnitOfWork) -> MemoryMessageBus:
    translocator = Translocator(
        inbox_path=config.inbox_path,
        workspaces_path=config.workspaces_path,
        minter=minter,
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
        ]
    }
    message_bus = MemoryMessageBus(handlers)
    return message_bus
