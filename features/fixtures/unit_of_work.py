import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dor.adapters.sqlalchemy import Base
from dor.config import config
from dor.service_layer.unit_of_work import AbstractUnitOfWork, SqlalchemyUnitOfWork

from gateway.ocfl_repository_gateway import OcflRepositoryGateway


@pytest.fixture
def unit_of_work() -> AbstractUnitOfWork:
    engine = create_engine(config.get_database_engine_url())
    connection = engine.connect()
    session_factory = sessionmaker(bind=connection)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    gateway = OcflRepositoryGateway(storage_path=config.storage_path)

    return SqlalchemyUnitOfWork(gateway=gateway, session_factory=session_factory)
