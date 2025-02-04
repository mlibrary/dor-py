import uuid
from datetime import datetime, UTC

import pytest
from pydantic_core import to_jsonable_python

from dor.service_layer.catalog_service import summarize, get_file_sets
from dor.domain.models import Bin
from dor.providers.models import (
    Agent, AlternateIdentifier, FileMetadata, FileReference, PackageResource,
    PreservationEvent, StructMap, StructMapItem, StructMapType
)

@pytest.mark.usefixtures("sample_bin")
def test_catalog_generates_summary(sample_bin):
    expected_summary = to_jsonable_python(dict(
        identifier=sample_bin.identifier,
        alternate_identifiers=sample_bin.alternate_identifiers,
        common_metadata=sample_bin.common_metadata,
    ))
    summary = summarize(sample_bin)
    assert expected_summary == summary

@pytest.mark.usefixtures("sample_bin")
def test_catalog_lists_file_sets(sample_bin):
    file_sets = get_file_sets(sample_bin)
    expected_file_sets = [
        to_jsonable_python(resource) 
        for resource in sample_bin.package_resources if resource.type == 'Asset'
    ]

    assert file_sets == expected_file_sets

def test_catalog_has_empty_file_sets():
    no_file_sets_bin = Bin(
        identifier=uuid.UUID("00000000-0000-0000-0000-000000000001"), 
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
                alternate_identifier=AlternateIdentifier(id="xyzzy:00000001", type="DLXS"),
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
                        use="DESCRIPTIVE/COMMON",
                        ref=FileReference(
                            locref="../metadata/00000000-0000-0000-0000-000000000001.common.json",
                            mdtype="DOR:SCHEMA",
                            mimetype="application/json",
                        ),
                    ),
                    FileMetadata(
                        id="_0193d5f0-7f65-783e-b7b4-485b6f6b24d0",
                        use="DESCRIPTIVE",
                        ref=FileReference(
                            locref="../metadata/00000000-0000-0000-0000-000000000001.metadata.json",
                            mdtype="DOR:SCHEMA",
                            mimetype="application/json",
                        ),
                    ),
                    FileMetadata(
                        id="RIGHTS1",
                        use="RIGHTS",
                        ref=FileReference(
                            locref="https://creativecommons.org/publicdomain/zero/1.0/",
                            mdtype="OTHER",
                        ),
                    ),
                ],
                struct_maps=[
                    StructMap(
                        id="SM1",
                        type=StructMapType.PHYSICAL,
                        items=[
                            StructMapItem(
                                order=1,
                                type="page",
                                label="Page 1",
                                asset_id="urn:dor:00000000-0000-0000-0000-000000001001",
                            ),
                            StructMapItem(
                                order=2,
                                type="page",
                                label="Page 2",
                                asset_id="urn:dor:00000000-0000-0000-0000-000000001002",
                            ),
                        ],
                    )
                ],
            )
        ]
    )

    file_sets = get_file_sets(no_file_sets_bin)
    assert file_sets == []
