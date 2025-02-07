from gateway.fake_repository_gateway import FakeRepositoryGateway
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dor.adapters.catalog import SqlalchemyCatalog
from dor.adapters.sqlalchemy import Base, _custom_json_serializer
from dor.config import config
from dor.service_layer.unit_of_work import SqlalchemyUnitOfWork


def setup_function() -> None:
    engine = create_engine(config.get_test_database_engine_url())
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


@pytest.fixture
def session_factory():
    return sessionmaker(bind=create_engine(
        config.get_test_database_engine_url(), json_serializer=_custom_json_serializer
    ))


@pytest.mark.usefixtures("sample_revision")
def test_uow_can_add_revision(session_factory, sample_revision):
    gateway = FakeRepositoryGateway()
    uow = SqlalchemyUnitOfWork(gateway=gateway, session_factory=session_factory)
    with uow:
        uow.catalog.add(sample_revision)
        uow.commit()
    
    session = session_factory()
    with session:
        catalog = SqlalchemyCatalog(session)
        revision = catalog.get(sample_revision.identifier)
    assert revision == sample_revision


@pytest.mark.usefixtures("sample_revision")
def test_uow_does_not_add_revision_without_commit(session_factory, sample_revision):
    gateway = FakeRepositoryGateway()
    uow = SqlalchemyUnitOfWork(gateway=gateway, session_factory=session_factory)
    with uow:
        uow.catalog.add(sample_revision)
    
    session = session_factory()
    with session:
        catalog = SqlalchemyCatalog(session)
        revision = catalog.get(sample_revision.identifier)
    assert revision is None
