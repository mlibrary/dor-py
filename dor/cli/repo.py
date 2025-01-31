import uuid
from typing import Callable, Type, Tuple

import typer
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
    PackageUnpacked,
    PackageVerified,
)
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.package_resource_provider import PackageResourceProvider
from dor.providers.translocator import Translocator, Workspace
from dor.service_layer.handlers.catalog_bin import catalog_bin
from dor.service_layer.handlers.receive_package import receive_package
from dor.service_layer.handlers.store_files import store_files
from dor.service_layer.handlers.unpack_package import unpack_package
from dor.service_layer.handlers.verify_package import verify_package
from dor.service_layer.message_bus.memory_message_bus import MemoryMessageBus
from dor.service_layer.unit_of_work import SqlalchemyUnitOfWork
from gateway.ocfl_repository_gateway import OcflRepositoryGateway


app = typer.Typer()


def bootstrap() -> Tuple[MemoryMessageBus, SqlalchemyUnitOfWork]:
    gateway = OcflRepositoryGateway(storage_path=config.storage_path)
 
    engine = create_engine(
        config.get_database_engine_url(), json_serializer=_custom_json_serializer
    )
    session_factory = sessionmaker(bind=engine)
    uow = SqlalchemyUnitOfWork(gateway=gateway, session_factory=session_factory)

    translocator = Translocator(
        inbox_path=config.inbox_path,
        workspaces_path=config.workspaces_path,
        minter = lambda: str(uuid.uuid4())
    )
    file_provider = FilesystemFileProvider()

    handlers: dict[Type[Event], list[Callable]] = {
        PackageSubmitted: [lambda event: receive_package(event, uow, translocator)],
        PackageReceived: [lambda event: verify_package(event, uow, BagAdapter, Workspace, file_provider)],
        PackageVerified: [
            lambda event: unpack_package(
                event, uow, BagAdapter, PackageResourceProvider, Workspace, file_provider
            )
        ],
        PackageUnpacked: [lambda event: store_files(event, uow, Workspace)],
        PackageStored: [lambda event: catalog_bin(event, uow)],
        BinCataloged: []
    }
    message_bus = MemoryMessageBus(handlers)
    return (message_bus, uow)


@app.command()
def initialize():
    gateway = OcflRepositoryGateway(storage_path=config.storage_path)
    gateway.create_repository()

    engine = create_engine(
        config.get_database_engine_url(), json_serializer=_custom_json_serializer
    )
    Base.metadata.create_all(engine)


@app.command()
def store(
    package_identifier: str = typer.Option(help="Name of the package directory"),
):
    message_bus, uow = bootstrap()
    event = PackageSubmitted(package_identifier=package_identifier)
    message_bus.handle(event, uow)
