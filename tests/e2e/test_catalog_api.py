import uuid
import pytest

from dor.adapters.catalog import SqlalchemyCatalog
from dor.adapters.converter import converter
from dor.builders.parts import UseFunction
from dor.domain.models import Revision
from dor.providers.models import AlternateIdentifier
from dor.service_layer.catalog_service import summarize_with_file_sets


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


@pytest.mark.usefixtures("sample_revision", "referenced_revision", "db_session", "test_client")
def test_catalog_api_returns_200_and_index_by_file_set(
    sample_revision: Revision, referenced_revision: Revision, db_session, test_client
) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()
    with db_session.begin():
        catalog.add(referenced_revision)
        db_session.commit()

    file_set_identifier = "00000000-0000-0000-0000-000000001001"
    response = test_client.get(f"/api/v1/catalog/revisions/index/{file_set_identifier}")

    assert response.status_code == 200

    referenced_file_set_identifier = AlternateIdentifier(
        type=UseFunction.copy_of.value,
        id=file_set_identifier
    )
    expected_mapping = {
        file_set_identifier: [
            dict(
                bin_identifier=str(sample_revision.identifier),
                file_set_identifier=file_set_identifier
            ),
            dict(
                bin_identifier=str(referenced_revision.identifier),
                file_set_identifier=str(
                    [resource for resource in referenced_revision.package_resources if referenced_file_set_identifier in resource.alternate_identifiers][0].id)
            ),
        ]
    }

    assert response.json() == expected_mapping


@pytest.mark.usefixtures("sample_revision", "referenced_revision", "db_session", "test_client")
def test_catalog_search_with_file_sets(sample_revision, referenced_revision, db_session, test_client
) -> None:
    file_set_identifier = "00000000-0000-0000-0000-000000001001"

    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()
    with db_session.begin():
        catalog.add(referenced_revision)
        db_session.commit()

    file_set_identifier = "00000000-0000-0000-0000-000000001001"
    response = test_client.get(f"/api/v1/catalog/revisions/search/file_set/{file_set_identifier}")

    assert response.status_code == 200

    referenced_file_set_identifier = AlternateIdentifier(
        type=UseFunction.copy_of.value,
        id=file_set_identifier
    )
    expected_summaries = [
        converter.unstructure(dict(
            identifier=sample_revision.identifier,
            revision_number=sample_revision.revision_number,
            created_at=sample_revision.created_at,
            alternate_identifiers=sample_revision.alternate_identifiers,
            common_metadata=sample_revision.common_metadata,
            file_sets=[
                str(resource.id)
                for resource in sample_revision.package_resources
                if str(resource.id) == file_set_identifier or referenced_file_set_identifier in resource.alternate_identifiers
            ]
        )),
        converter.unstructure(dict(
            identifier=referenced_revision.identifier,
            revision_number=referenced_revision.revision_number,
            created_at=referenced_revision.created_at,
            alternate_identifiers=referenced_revision.alternate_identifiers,
            common_metadata=referenced_revision.common_metadata,
            file_sets=[
                str(resource.id)
                for resource in referenced_revision.package_resources
                if resource.id == file_set_identifier or referenced_file_set_identifier in resource.alternate_identifiers
            ]
        )),
    ]

    print(response.json())

    assert response.json() == expected_summaries
