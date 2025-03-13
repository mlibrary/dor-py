import pytest

from dor.adapters.catalog import SqlalchemyCatalog
from dor.adapters.converter import converter
from dor.domain.models import Revision


@pytest.mark.usefixtures("sample_revision", "db_session", "test_client")
def test_catalog_api_returns_200_and_summary(
    sample_revision: Revision, db_session, test_client
) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()

    response = test_client.get(f"/api/v1/catalog/revisions/{sample_revision.identifier}/")

    assert response.status_code == 200
    expected_summary = converter.unstructure(dict(
        identifier=sample_revision.identifier,
        alternate_identifiers=sample_revision.alternate_identifiers,
        revision_number=sample_revision.revision_number,
        created_at=sample_revision.created_at,
        common_metadata=sample_revision.common_metadata,
    ))
    assert response.json() == expected_summary


@pytest.mark.usefixtures("sample_revision", "db_session", "test_client")
def test_catalog_api_returns_200_and_file_sets(
    sample_revision: Revision, db_session, test_client
) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()

    response = test_client.get(f"/api/v1/catalog/revisions/{sample_revision.identifier}/filesets")

    assert response.status_code == 200
    expected_file_sets = converter.unstructure([sample_revision.package_resources[1]])
    assert response.json() == expected_file_sets
