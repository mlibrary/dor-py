import os

import pytest
import sqlalchemy
from pydantic_core import to_jsonable_python
from fastapi.testclient import TestClient

from dor.adapters.catalog import SqlalchemyCatalog
from dor.domain.models import Bin
from dor.entrypoints.api.main import app


def get_api_url() -> str:
    return os.environ["URL"] + "/api/v1"


def get_test_client() -> TestClient:
    return TestClient(app)


@pytest.mark.usefixtures("db_session", "sample_bin")
def test_catalog_api_returns_201_and_summary(
    db_session: sqlalchemy.orm.Session, sample_bin: Bin
) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_bin)
        db_session.commit()

    test_client = get_test_client()
    response = test_client.get(get_api_url() + f"/catalog/bins/{sample_bin.identifier}/")

    assert response.status_code == 200
    expected_summary = to_jsonable_python(dict(
        identifier=sample_bin.identifier,
        alternate_identifiers=sample_bin.alternate_identifiers,
        common_metadata=sample_bin.common_metadata,
    ))
    assert response.json() == expected_summary

@pytest.mark.usefixtures("db_session", "sample_bin")
def test_catalog_api_returns_201_and_file_sets(
    db_session: sqlalchemy.orm.Session, sample_bin: Bin
) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_bin)
        db_session.commit()

    test_client = get_test_client()
    response = test_client.get(get_api_url() + f"/catalog/bins/{sample_bin.identifier}/filesets")

    assert response.status_code == 200
    expected_summary = to_jsonable_python([sample_bin.package_resources[1]])
    assert response.json() == expected_summary
