import uuid
from datetime import datetime, UTC
from pathlib import Path
from enum import Enum
import pytest

from dor.providers.models import (
    Agent,
    AlternateIdentifier,
    FileMetadata,
    FileReference,
    PackageResource,
    PreservationEvent,
    StructMap,
    StructMapItem,
    StructMapType,
)
from dor.providers.package_resources_merger import PackageResourcesMerger


@pytest.fixture
def current() -> list[PackageResource]:
    return [
        PackageResource(
            id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            type="Monograph",
            alternate_identifiers=[AlternateIdentifier(id="xyzzy:00000001", type="DLXS")],
            events=[
                PreservationEvent(
                    identifier="23b04e8b-f7fd-4331-a3bb-0157f9a057d6",
                    type="ingest",
                    datetime=datetime(1974, 6, 24, 1, 8, 39, tzinfo=UTC),
                    detail="This front attack nature.",
                    agent=Agent(
                        address="steven34@example.net",
                        role="collection manager",
                    ),
                )
            ],
            metadata_files=[
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000000101",
                    use="function:service",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.function:service.json",
                        mdtype="schema:common",
                        mimetype="application/json+schema",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000000102",
                    use="function:source",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.function:source.json",
                        mdtype="schema:monograph",
                        mimetype="application/json+schema",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000000103",
                    use="function:provenancne",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.function:provenance.premis.xml",
                        mdtype="PREMIS",
                        mimetype="text/xml+premis",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000000104",
                    use="function:event",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.function:event.premis.xml",
                        mdtype="PREMIS",
                        mimetype="text/xml+premis",
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


@pytest.fixture
def incoming() -> list[PackageResource]:
    return [
        PackageResource(
            id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            type="Monograph",
            alternate_identifiers=[AlternateIdentifier(id="xyzzy:00000001", type="DLXS")],
            events=[
                PreservationEvent(
                    identifier="94032aff-e1a9-4c1b-8066-3e153f57df67",
                    type="ingest",
                    datetime=datetime(1976, 10, 31, 23, 59, 59, tzinfo=UTC),
                    detail="Boo.",
                    agent=Agent(
                        address="ghost@example.net",
                        role="collection manager",
                    ),
                )
            ],
            metadata_files=[
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000000101",
                    use="function:service",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.function:service.json",
                        mdtype="schema:common",
                        mimetype="application/json+schema",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000000102",
                    use="function:source",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.function:source.json",
                        mdtype="schema:monograph",
                        mimetype="application/json+schema",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000000103",
                    use="function:provenance",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.function:provenance.premis.xml",
                        mdtype="PREMIS",
                        mimetype="text/xml+premis",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000000104",
                    use="function:event",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.function:event.premis.xml",
                        mdtype="PREMIS",
                        mimetype="text/xml+premis",
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
                            file_set_id="00000000-0000-0000-0000-000000001001",
                        ),
                        StructMapItem(
                            order=2,
                            type="structure:page",
                            label="Page 2",
                            file_set_id="00000000-0000-0000-0000-000000001002",
                        ),
                    ],
                )
            ],
        )
    ]


@pytest.fixture
def partial() -> list[PackageResource]:
    return [
        PackageResource(
            id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            type="Monograph",
            alternate_identifiers=[AlternateIdentifier(id="xyzzy:00000001", type="DLXS")],
            events=[
                PreservationEvent(
                    identifier="5c6a593d-afb8-49da-a91a-c12c91cfb4e8",
                    type="ingest",
                    datetime=datetime(1977, 1, 1, 0, 0, 0, tzinfo=UTC),
                    detail="Happy New Year.",
                    agent=Agent(
                        address="fathertime@example.net",
                        role="collection manager",
                    ),
                )
            ],
            metadata_files=[
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000000101",
                    use="function:service",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.function:service.json",
                        mdtype="schema:common",
                        mimetype="application/json+schema",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000000102",
                    use="function:source",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.function:source.json",
                        mdtype="schema:monograph",
                        mimetype="application/json+schema",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000000110",
                    use="function:random",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.random.xml",
                        mdtype="schema:random",
                        mimetype="text/xml",
                    ),
                ),
            ],
            struct_maps=[
                StructMap(
                    id="SM1",
                    type=StructMapType.manifest,
                    items=[
                        StructMapItem(
                            order=1,
                            type="structure:page",
                            label="Page 1",
                            file_set_id="00000000-0000-0000-0000-000000001001",
                        ),
                    ],
                )
            ],
        )
    ]


def test_merging_complete_resources(current: list[PackageResource], incoming: list[PackageResource]):
    merger = PackageResourcesMerger(current=current, incoming=incoming)
    results = merger.merge_changes()

    assert results[0].metadata_files == incoming[0].metadata_files
    assert results[0].events == (current[0].events + incoming[0].events)


def test_merging_partial_resources(current: list[PackageResource], partial: list[PackageResource]):
    merger = PackageResourcesMerger(current=current, incoming=partial)
    results = merger.merge_changes()
    assert len(results[0].metadata_files) == 5
    assert results[0].struct_maps == current[0].struct_maps
