import os
import shutil
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Callable, Type

import pytest
from pytest_bdd import scenario, given, when, then
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dor.adapters.bag_adapter import BagAdapter
from dor.adapters.catalog import Base, _custom_json_serializer
from dor.config import config
from dor.domain.events import (
    Event,
    BinCataloged,
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
from dor.service_layer.unit_of_work import AbstractUnitOfWork, SqlalchemyUnitOfWork
from gateway.ocfl_repository_gateway import OcflRepositoryGateway
from dor.service_layer.handlers.catalog_bin import catalog_bin
from dor.service_layer.handlers.receive_package import receive_package
from dor.service_layer.handlers.verify_package import verify_package
from dor.service_layer.handlers.unpack_package import unpack_package

@dataclass
class Context:
    message_bus: MemoryMessageBus | None = None
    cataloged_event: BinCataloged | None = None

@pytest.fixture
def storage_path() -> Path:
    return Path("./features/scratch/storage")

@pytest.fixture
def unit_of_work(storage_path: Path) -> AbstractUnitOfWork:
    engine = create_engine(
        config.get_test_database_engine_url(), json_serializer=_custom_json_serializer
    )
    session_factory = sessionmaker(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    gateway = OcflRepositoryGateway(storage_path=storage_path)

    return SqlalchemyUnitOfWork(gateway=gateway, session_factory=session_factory)


scenario = partial(scenario, '../store_resource.feature')

@scenario('Storing a new resource for immediate release')
def test_store_resource():
    pass

@given(u'a package containing the scanned pages, OCR, and metadata', target_fixture="context")
def _(storage_path: Path, unit_of_work: AbstractUnitOfWork):
    context = Context()

    scratch = Path("./features/scratch")    
    shutil.rmtree(path = scratch, ignore_errors = True)
    os.mkdir(scratch)

    os.mkdir(storage_path)

    unit_of_work.gateway.create_repository()

    inbox = Path("./features/fixtures/inbox")

    workspaces = Path("./features/scratch/workspaces")
    os.mkdir(workspaces)

    value = "55ce2f63-c11a-4fac-b3a9-160305b1a0c4"

    translocator = Translocator(inbox_path = inbox, workspaces_path = workspaces, minter = lambda: value)

    def cataloged_callback(event: BinCataloged, uow: AbstractUnitOfWork) -> None:
        context.cataloged_event = event

    handlers: dict[Type[Event], list[Callable]] = {
        PackageSubmitted: [
            lambda event: receive_package(event, unit_of_work, translocator)
        ],
        PackageReceived: [
            lambda event: verify_package(event, unit_of_work, BagAdapter, Workspace)
        ],
        PackageVerified: [
            lambda event: unpack_package(
                event,
                unit_of_work,
                BagAdapter,
                PackageResourceProvider,
                Workspace,
                FilesystemFileProvider(),
            )
        ],
        PackageUnpacked: [lambda event: store_files(event, unit_of_work, Workspace)],
        PackageStored: [lambda event: catalog_bin(event, unit_of_work)],
        BinCataloged: [lambda event: cataloged_callback(event, unit_of_work)]
    }
    context.message_bus = MemoryMessageBus(handlers)
    return context

@when(u'the Collection Manager places the packaged resource in the incoming location')
def _(context, unit_of_work: AbstractUnitOfWork):
    submission_id = "xyzzy-0001-v1"

    event = PackageSubmitted(package_identifier=submission_id)
    context.message_bus.handle(event, unit_of_work)

@then(u'the Collection Manager can see that it was preserved.')
def _(context, unit_of_work: AbstractUnitOfWork):
    event = context.cataloged_event
    assert event.identifier == "00000000-0000-0000-0000-000000000001"
    assert unit_of_work.gateway.has_object(event.identifier)

    with unit_of_work:
        bin = unit_of_work.catalog.get(event.identifier)
        assert bin is not None
