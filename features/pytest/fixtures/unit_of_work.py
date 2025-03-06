import pytest

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dor.adapters.sqlalchemy import Base, _custom_json_serializer
from dor.config import config
from dor.domain.models import PathData
from dor.service_layer.unit_of_work import AbstractUnitOfWork, SqlalchemyUnitOfWork

from gateway.ocfl_repository_gateway import OcflRepositoryGateway


@pytest.fixture
def unit_of_work(path_data: PathData) -> Generator[AbstractUnitOfWork, None, None]:
    engine = create_engine(
        config.get_test_database_engine_url(), json_serializer=_custom_json_serializer
    )
    connection = engine.connect()
    session_factory = sessionmaker(bind=connection)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    gateway = OcflRepositoryGateway(storage_path=path_data.storage)

    yield SqlalchemyUnitOfWork(gateway=gateway, session_factory=session_factory)

    connection.close()