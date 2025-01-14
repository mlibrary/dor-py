from typing import Generator

import pytest
import sqlalchemy
from pydantic_core import to_jsonable_python
from fastapi.testclient import TestClient

from dor.adapters.catalog import Base, SqlalchemyCatalog, _custom_json_serializer
from dor.config import config
from dor.domain.models import Bin
from dor.entrypoints.api.dependencies import get_db_session
from dor.entrypoints.api.main import app


@pytest.fixture
def db_session() -> Generator[sqlalchemy.orm.Session, None, None]:
    engine_url = config.get_test_database_engine_url()
    engine = sqlalchemy.create_engine(
        engine_url, echo=True, json_serializer=_custom_json_serializer
    )

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    connection = engine.connect()
    session = sqlalchemy.orm.Session(bind=connection)

    yield session

    session.close()
    connection.close()


@pytest.fixture
def test_client(db_session) -> Generator[TestClient, None, None]:
    def get_db_session_override():
        return db_session

    app.dependency_overrides[get_db_session] = get_db_session_override
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.mark.usefixtures("sample_bin")
def test_catalog_api_returns_200_and_summary(
    sample_bin: Bin, db_session, test_client
) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_bin)
        db_session.commit()

    response = test_client.get(f"/api/v1/catalog/bins/{sample_bin.identifier}/")

    assert response.status_code == 200
    expected_summary = to_jsonable_python(dict(
        identifier=sample_bin.identifier,
        alternate_identifiers=sample_bin.alternate_identifiers,
        common_metadata=sample_bin.common_metadata,
    ))
    assert response.json() == expected_summary


@pytest.mark.usefixtures("sample_bin")
def test_catalog_api_returns_200_and_file_sets(
    sample_bin: Bin, db_session, test_client
) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_bin)
        db_session.commit()

    response = test_client.get(f"/api/v1/catalog/bins/{sample_bin.identifier}/filesets")

    assert response.status_code == 200
    expected_summary = to_jsonable_python([sample_bin.package_resources[1]])
    assert response.json() == expected_summary
