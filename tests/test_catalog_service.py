import uuid
from datetime import datetime, UTC

import pytest

from dor.adapters.converter import converter
from dor.builders.parts import UseFunction
from dor.service_layer.catalog_service import summarize, get_file_sets, index_by_file_set, summarize_by_file_set
from dor.domain.models import Revision
from dor.providers.models import (
    Agent, AlternateIdentifier, FileMetadata, FileReference, PackageResource,
    PreservationEvent, StructMap, StructMapItem, StructMapType
)


@pytest.mark.usefixtures("sample_revision")
def test_catalog_generates_summary(sample_revision):
    expected_summary = converter.unstructure(dict(
        identifier=sample_revision.identifier,
        revision_number=sample_revision.revision_number,
        created_at=sample_revision.created_at,
        alternate_identifiers=sample_revision.alternate_identifiers,
        common_metadata=sample_revision.common_metadata,
    ))
    summary = summarize(sample_revision)
    assert expected_summary == summary


@pytest.mark.usefixtures("sample_revision")
def test_catalog_lists_file_sets(sample_revision):
    file_sets = get_file_sets(sample_revision)
    expected_file_sets = [
        converter.unstructure(resource)
        for resource in sample_revision.package_resources if resource.type == 'File Set'
    ]

    assert file_sets == expected_file_sets


def test_catalog_has_empty_file_sets():
    no_file_sets_revision = Revision(
        identifier=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        revision_number=1,
        created_at=datetime(2025, 2, 5, 12, 0, 0, 0, tzinfo=UTC),
        alternate_identifiers=["xyzzy:00000001"],
        common_metadata={
            "@schema": "urn:umich.edu:dor:schema:common",
            "title": "Discussion also Republican owner hot already itself.",
            "author": "Kimberly Garza",
            "publication_date": "1989-04-16",
            "subjects": [
                "Liechtenstein",
                "Vietnam",
            ]
        },
        package_resources=[
            PackageResource(
                id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                type="Monograph",
                root=True,
                alternate_identifiers=[AlternateIdentifier(id="xyzzy:00000001", type="DLXS")],
                events=[
                    PreservationEvent(
                        identifier="abdcb901-721a-4be0-a981-14f514236633",
                        type="ingest",
                        datetime=datetime(2016, 11, 29, 13, 51, 14, tzinfo=UTC),
                        detail="Middle president push visit information feel most.",
                        agent=Agent(
                            address="christopherpayne@example.org", role="collection manager"
                        ),
                    )
                ],
                metadata_files=[
                    FileMetadata(
                        id="_0193d5f0-7f64-7ac8-8f94-85c55c7313e4",
                        use="function:service",
                        ref=FileReference(
                            locref="../metadata/00000000-0000-0000-0000-000000000001.function:service.json",
                            mdtype="schema:common",
                            mimetype="application/json+schema",
                        ),
                    ),
                    FileMetadata(
                        id="_0193d5f0-7f65-783e-b7b4-485b6f6b24d0",
                        use="function:source",
                        ref=FileReference(
                            locref="../metadata/00000000-0000-0000-0000-000000000001.function:source.json",
                            mdtype="schema:monograph",
                            mimetype="application/json+schema",
                        ),
                    ),
                ],
                struct_maps=[
                    StructMap(
                        id="SM1",
                        type=StructMapType.physical,
                        items=[
                            StructMapItem(
                                order=1,
                                type="structure:page",
                                label="Page 1",
                                file_set_id="urn:dor:00000000-0000-0000-0000-000000001001",
                            ),
                            StructMapItem(
                                order=2,
                                type="structure:page",
                                label="Page 2",
                                file_set_id="urn:dor:00000000-0000-0000-0000-000000001002",
                            ),
                        ],
                    )
                ],
            )
        ]
    )

    file_sets = get_file_sets(no_file_sets_revision)
    assert file_sets == []


@pytest.mark.usefixtures("sample_revision", "referenced_revision")
def test_catalog_index_by_file_set(sample_revision, referenced_revision):
    file_set_identifier = "00000000-0000-0000-0000-000000001001"
    mapping = index_by_file_set([sample_revision, referenced_revision], uuid.UUID(file_set_identifier))

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

    assert expected_mapping == mapping


@pytest.mark.usefixtures("sample_revision", "referenced_revision")
def test_catalog_search_with_file_sets(sample_revision, referenced_revision):
    file_set_identifier = "00000000-0000-0000-0000-000000001001"
    summaries = summarize_by_file_set([sample_revision, referenced_revision], uuid.UUID(file_set_identifier))

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

    assert expected_summaries == summaries
