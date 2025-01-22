import os
import shutil
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Type

from functools import partial
from pytest_bdd import scenario, given, when, then

from dor.adapters.bag_adapter import BagAdapter
from dor.domain.events import (
    Event,
    PackageReceived,
    PackageStored,
    PackageSubmitted,
    PackageVerified,
    PackageUnpacked
)
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.translocator import Translocator, Workspace
from dor.providers.package_resource_provider import PackageResourceProvider
from dor.service_layer.handlers.store_files import store_files
from dor.service_layer.message_bus.memory_message_bus import MemoryMessageBus
from dor.service_layer.unit_of_work import UnitOfWork
from gateway.ocfl_repository_gateway import OcflRepositoryGateway
from dor.service_layer.handlers.receive_package import receive_package
from dor.service_layer.handlers.verify_package import verify_package
from dor.service_layer.handlers.unpack_package import unpack_package

@dataclass
class Context:
    uow: UnitOfWork = None
    translocator: Translocator = None
    message_bus: MemoryMessageBus = None
    stored_event: PackageStored = None


scenario = partial(scenario, '../store_resource.feature')

@scenario('Storing a new resource for immediate release')
def test_store_resource():
    pass

@given(u'a package containing the scanned pages, OCR, and metadata', target_fixture="context")
def _():
    context = Context()

    inbox = Path("./features/fixtures/inbox")
    storage = Path("./features/scratch/storage")
    workspaces = Path("./features/scratch/workspaces")

    value = "55ce2f63-c11a-4fac-b3a9-160305b1a0c4"

    shutil.rmtree(path = f"./features/scratch/workspaces/{value}", ignore_errors = True)
    shutil.rmtree(path = storage, ignore_errors = True)
    os.mkdir(storage)

    gateway = OcflRepositoryGateway(storage_path = storage)
    gateway.create_repository()
    context.uow = UnitOfWork(gateway=gateway)

    context.translocator = Translocator(inbox_path = inbox, workspaces_path = workspaces, minter = lambda: value)

    def stored_callback(event: PackageStored, uow: UnitOfWork) -> None:
        context.stored_event = event

    handlers: dict[Type[Event], list[Callable]] = {
        PackageSubmitted: [
            lambda event: receive_package(event, context.uow, context.translocator)
        ],
        PackageReceived: [
            lambda event: verify_package(event, context.uow, BagAdapter, Workspace)
        ],
        PackageVerified: [
            lambda event: unpack_package(
                event,
                context.uow,
                BagAdapter,
                PackageResourceProvider,
                Workspace,
                FilesystemFileProvider(),
            )
        ],
        PackageUnpacked: [lambda event: store_files(event, context.uow, Workspace)],
        PackageStored: [lambda event: stored_callback(event, context.uow)]
    }
    context.message_bus = MemoryMessageBus(handlers)
    return context

@when(u'the Collection Manager places the packaged resource in the incoming location')
def _(context):
    submission_id = "xyzzy-0001-v1"

    event = PackageSubmitted(package_identifier=submission_id)
    context.message_bus.handle(event, context.uow)

@then(u'the Collection Manager can see that it was preserved.')
def _(context):
    event = context.stored_event
    assert event.identifier == "00000000-0000-0000-0000-000000000001"
    assert context.uow.gateway.has_object(event.identifier)