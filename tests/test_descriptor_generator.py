import os
import shutil
from pathlib import Path
import uuid
import pytest
from datetime import datetime, UTC

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

from dor.providers.translocator import Workspace
from dor.providers.descriptor_generator import DescriptorGenerator

@pytest.fixture
def sample_resources():
    return [
        PackageResource(
            id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            type="Monograph",
            root=True,
            alternate_identifier=AlternateIdentifier(id="xyzzy:00000001", type="DLXS"),
            events=[
                PreservationEvent(
                    identifier="abdcb901-721a-4be0-a981-14f514236633",
                    type="ingest",
                    datetime=datetime(2016, 11, 29, 13, 51, 14, tzinfo=UTC),
                    detail="Middle president push visit information feel most.",
                    agent=Agent(
                        address="christopherpayne@example.org",
                        role="collection manager",
                    ),
                )
            ],
            metadata_files=[
                FileMetadata(
                    id="_0193d5f0-7f64-7ac8-8f94-85c55c7313e4",
                    use="DESCRIPTIVE/COMMON",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.common.json",
                        mdtype="DOR:SCHEMA",
                        mimetype="application/json",
                    ),
                ),
                FileMetadata(
                    id="_0193d5f0-7f65-783e-b7b4-485b6f6b24d0",
                    use="DESCRIPTIVE",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.metadata.json",
                        mdtype="DOR:SCHEMA",
                        mimetype="application/json",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000000103",
                    use="PROVENANCE",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.premis.object.xml",
                        mdtype="PREMIS",
                        mimetype="text/xml",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000000104",
                    use="EVENT",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.premis.event.xml",
                        mdtype="PREMIS",
                        mimetype="text/xml",
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
                        )
                    ],
                )
            ],
        ),
        PackageResource(
            id=uuid.UUID("00000000-0000-0000-0000-000000001001"),
            type="File Set",
            alternate_identifier=AlternateIdentifier(
                id="xyzzy:00000001:00000001", type="DLXS"
            ),
            events=[
                PreservationEvent(
                    identifier="fe4c76e5-dbf1-4934-97fb-52ef5a68f073",
                    type="generate access derivative",
                    datetime=datetime(1993, 6, 11, 4, 44, 7, tzinfo=UTC),
                    detail="Night wonder three him family structure simple.",
                    agent=Agent(
                        address="arroyoalan@example.net", role="image processing"
                    ),
                ),
                PreservationEvent(
                    identifier="3bdcb1e3-4674-4b9c-83c8-4f9f9fe50812",
                    type="extract text",
                    datetime=datetime(1988, 5, 26, 18, 33, 46, tzinfo=UTC),
                    detail="Player center road attorney speak wait partner.",
                    agent=Agent(
                        address="jonathanjones@example.net", role="ocr processing"
                    ),
                ),
            ],
            metadata_files=[
                FileMetadata(
                    id="_0193d5f0-7e72-7481-b6fd-0f916c30b396",
                    use="TECHNICAL",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.source.jpg.mix.xml",
                        mdtype="NISOIMG",
                    ),
                ),
                FileMetadata(
                    id="_0193d5f0-7e75-7803-8e41-71323b7b3284",
                    group_id="_0193d5f0-7e72-7481-b6fd-0f916c30b396",
                    use="TECHNICAL",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.access.jpg.mix.xml",
                        mdtype="NISOIMG",
                    ),
                ),
                FileMetadata(
                    id="_0193d5f0-7f54-7268-b9b1-821085acdcf7",
                    group_id="_0193d5f0-7e72-7481-b6fd-0f916c30b396",
                    use="TECHNICAL",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.plaintext.txt.textmd.xml",
                        mdtype="TEXTMD",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000100103",
                    use="EVENT",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.access.jpg.premis.event.xml",
                        mdtype="PREMIS",
                    ),
                ),
            ],
            data_files=[
                FileMetadata(
                    id="_be653ff450ae7f3520312a53e56c00bc",
                    mdid="_0193d5f0-7e72-7481-b6fd-0f916c30b396",
                    use="SOURCE",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/data/00000001.source.jpg",
                        mimetype="image/jpeg",
                    ),
                ),
                FileMetadata(
                    id="_7e923d9c33b3859e1327fa53a8e609a1",
                    groupid="_be653ff450ae7f3520312a53e56c00bc",
                    mdid="_0193d5f0-7e75-7803-8e41-71323b7b3284",
                    use="ACCESS",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/data/00000001.access.jpg",
                        mimetype="image/jpeg",
                    ),
                ),
                FileMetadata(
                    id="_764ba9761fbc6cbf0462d28d19356148",
                    groupid="_be653ff450ae7f3520312a53e56c00bc",
                    mdid="_0193d5f0-7f54-7268-b9b1-821085acdcf7",
                    use="SOURCE",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/data/00000001.plaintext.txt",
                        mimetype="text/plain",
                    ),
                ),
            ],
        ),
    ]

def test_generator_can_create_descriptor_files(sample_resources):
    package_path = Path("./tests/test_workspaces")
    shutil.rmtree(package_path, ignore_errors=True)
    os.makedirs(package_path / "descriptor")

    generator = DescriptorGenerator(package_path=package_path, resources=sample_resources)
    generator.write_files()

    assert (package_path / "00000000-0000-0000-0000-000000000001" / "descriptor" / "00000000-0000-0000-0000-000000000001.monograph.mets2.xml" ).exists()
    assert (package_path / "00000000-0000-0000-0000-000000001001" / "descriptor" / "00000000-0000-0000-0000-000000001001.file_set.mets2.xml" ).exists()

def test_generator_can_return_entries(sample_resources):
    package_path = Path("./tests/test_workspaces")
    shutil.rmtree(package_path, ignore_errors=True)
    os.makedirs(package_path / "descriptor")

    generator = DescriptorGenerator(package_path=package_path, resources=sample_resources)
    generator.write_files()

    entries = generator.entries
    assert entries == [
        Path(
            "00000000-0000-0000-0000-000000000001/descriptor/00000000-0000-0000-0000-000000000001.monograph.mets2.xml"
        ),
        Path(
            "00000000-0000-0000-0000-000000001001/descriptor/00000000-0000-0000-0000-000000001001.file_set.mets2.xml"
        ),
    ]
