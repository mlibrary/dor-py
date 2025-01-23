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
from dor.providers.package_resource_provider import PackageResourceProvider
from dor.providers.translocator import Translocator, Workspace
from dor.service_layer.handlers.catalog_bin import catalog_bin
from dor.service_layer.handlers.receive_package import receive_package
from dor.service_layer.handlers.store_files import store_files
from dor.service_layer.handlers.unpack_package import unpack_package
from dor.service_layer.handlers.verify_package import verify_package
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
    scratch = Path("./features/scratch")

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
        minter = lambda: value
    )

    handlers: dict[Type[Event], list[Callable]] = {
        PackageSubmitted: [lambda event: receive_package(event, unit_of_work, translocator)],
        PackageReceived: [lambda event: verify_package(event, unit_of_work, BagAdapter, Workspace)],
        PackageVerified: [lambda event: unpack_package(
            event, unit_of_work, BagAdapter, PackageResourceProvider, Workspace
        )],
        PackageUnpacked: [lambda event: store_files(event, unit_of_work, Workspace)],
        PackageStored: [lambda event: catalog_bin(event, unit_of_work)],
        BinCataloged: []
    }
    message_bus = MemoryMessageBus(handlers)
    return message_bus

scenario = partial(scenario, '../store_resource.feature')

@scenario('Storing a new resource for immediate release')
def test_store_resource():
    pass

@given(u'a package containing the scanned pages, OCR, and metadata')
def _(path_data: PathData, unit_of_work: AbstractUnitOfWork):
    shutil.rmtree(path=path_data.scratch, ignore_errors = True)
    os.mkdir(path_data.scratch)
    os.mkdir(path_data.storage)
    os.mkdir(path_data.workspaces)

    unit_of_work.gateway.create_repository()

@when(u'the Collection Manager places the packaged resource in the incoming location')
def _(message_bus: MemoryMessageBus, unit_of_work: AbstractUnitOfWork):
    submission_id = "xyzzy-0001-v1"

    event = PackageSubmitted(package_identifier=submission_id)
    message_bus.handle(event, unit_of_work)

@then(u'the Collection Manager can see that it was preserved.')
def _(unit_of_work: AbstractUnitOfWork):
    expected_identifier = "00000000-0000-0000-0000-000000000001"
    assert unit_of_work.gateway.has_object(expected_identifier)

    with unit_of_work:
        bin = unit_of_work.catalog.get(expected_identifier)
        assert bin is not None
