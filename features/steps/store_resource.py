import os
import shutil
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Type

from behave import given, when, then

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from dor.adapters.catalog import Base, _custom_json_serializer
from dor.config import config

from dor.adapters.bag_adapter import BagAdapter
from dor.domain.events import (
    Event,
    PackageReceived,
    PackageStored,
    PackageSubmitted,
    PackageVerified,
    PackageUnpacked,
    BinCataloged,
)
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.translocator import Translocator, Workspace
from dor.providers.package_resource_provider import PackageResourceProvider
from dor.service_layer.handlers.store_files import store_files
from dor.service_layer.message_bus.memory_message_bus import MemoryMessageBus
from dor.service_layer.unit_of_work import UnitOfWork, SqlalchemyUnitOfWork
from gateway.ocfl_repository_gateway import OcflRepositoryGateway
from dor.service_layer.handlers.receive_package import receive_package
from dor.service_layer.handlers.verify_package import verify_package
from dor.service_layer.handlers.unpack_package import unpack_package
from dor.service_layer.handlers.catalog_bin import catalog_bin

# Test


@given("a package containing the scanned pages, OCR, and metadata")
def step_impl(context) -> None:
    inbox = Path("./features/fixtures/inbox")
    storage = Path("./features/scratch/storage")
    workspaces = Path("./features/scratch/workspaces")

    value = "55ce2f63-c11a-4fac-b3a9-160305b1a0c4"

    shutil.rmtree(path=f"./features/scratch/workspaces/{value}", ignore_errors=True)
    shutil.rmtree(path=storage, ignore_errors=True)
    os.mkdir(storage)

    gateway = OcflRepositoryGateway(storage_path=storage)
    gateway.create_repository()
 
    engine = create_engine(
        config.get_test_database_engine_url(), json_serializer=_custom_json_serializer
    )
    session_factory = sessionmaker(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    context.uow = SqlalchemyUnitOfWork(gateway=gateway, session_factory=session_factory)

    context.translocator = Translocator(inbox_path = inbox, workspaces_path = workspaces, minter = lambda: value)

    def cataloged_callback(event: BinCataloged, uow: UnitOfWork) -> None:
        context.cataloged_event = event

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
        PackageStored: [lambda event: catalog_bin(event, context.uow)],
        BinCataloged: [lambda event: cataloged_callback(event, context.uow)]
    }
    context.message_bus = MemoryMessageBus(handlers)


@when("the Collection Manager places the packaged resource in the incoming location")
def step_impl(context):
    submission_id = "xyzzy-0001-v1"

    event = PackageSubmitted(package_identifier=submission_id)
    context.message_bus.handle(event, context.uow)


@then("the Collection Manager can see that it was preserved.")
def step_impl(context):
    event = context.cataloged_event
    assert event.identifier == "00000000-0000-0000-0000-000000000001"
    assert context.uow.gateway.has_object(event.identifier)

    with context.uow:
        bin = context.uow.catalog.get(event.identifier)
        assert bin is not None


