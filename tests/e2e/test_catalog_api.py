import pytest
from pydantic_core import to_jsonable_python

from dor.adapters.catalog import SqlalchemyCatalog
from dor.domain.models import Bin


@pytest.mark.usefixtures("sample_bin", "db_session", "test_client")
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


@pytest.mark.usefixtures("sample_bin", "db_session", "test_client")
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
