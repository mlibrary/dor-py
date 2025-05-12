import uuid
from datetime import datetime, UTC
from pathlib import Path

import pytest

from dor.providers.descriptor_generator import DescriptorGenerator
from dor.providers.file_system_file_provider import FilesystemFileProvider
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


@pytest.fixture
def sample_resources():
    return [
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
                        address="christopherpayne@example.org",
                        role="collection manager",
                    ),
                )
            ],
            metadata_files=[
                FileMetadata(
                    id="_0193d5f0-7f64-7ac8-8f94-85c55c7313e4",
                    use="function:service",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.function:service.json",
                        mdtype="schema:common",
                        mimetype="application/json+schema",
                    ),
                ),
                FileMetadata(
                    id="_0193d5f0-7f65-783e-b7b4-485b6f6b24d0",
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
                        )
                    ],
                )
            ],
        ),
        PackageResource(
            id=uuid.UUID("00000000-0000-0000-0000-000000001001"),
            type="File Set",
            alternate_identifiers=AlternateIdentifier(
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
                    use="function:technical",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.function:source.format:image.jpg.mix.xml",
                        mdtype="NISOIMG",
                    ),
                ),
                FileMetadata(
                    id="_0193d5f0-7e75-7803-8e41-71323b7b3284",
                    groupid="_0193d5f0-7e72-7481-b6fd-0f916c30b396",
                    use="function:technical",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.function:service.format:image.jpg.mix.xml",
                        mdtype="NISOIMG",
                    ),
                ),
                FileMetadata(
                    id="_0193d5f0-7f54-7268-b9b1-821085acdcf7",
                    groupid="_0193d5f0-7e72-7481-b6fd-0f916c30b396",
                    use="function:technical",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.function:service.format:text-plain.txt.textmd.xml",
                        mdtype="TEXTMD",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000100103",
                    use="function:event",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.function:service.format:image.jpg.function:event.premis.xml",
                        mdtype="PREMIS",
                    ),
                ),
            ],
            data_files=[
                FileMetadata(
                    id="_be653ff450ae7f3520312a53e56c00bc",
                    mdid="_0193d5f0-7e72-7481-b6fd-0f916c30b396",
                    use="function:source format:image",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/data/00000001.function:source.format:image.jpg",
                        mimetype="image/jpeg",
                    ),
                ),
                FileMetadata(
                    id="_7e923d9c33b3859e1327fa53a8e609a1",
                    groupid="_be653ff450ae7f3520312a53e56c00bc",
                    mdid="_0193d5f0-7e75-7803-8e41-71323b7b3284",
                    use="function:service format:image",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/data/00000001.function:service.format:image.jpg",
                        mimetype="image/jpeg",
                    ),
                ),
                FileMetadata(
                    id="_764ba9761fbc6cbf0462d28d19356148",
                    groupid="_be653ff450ae7f3520312a53e56c00bc",
                    mdid="_0193d5f0-7f54-7268-b9b1-821085acdcf7",
                    use="function:service format:text-plain",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/data/00000001.function:service.format:text-plain.txt",
                        mimetype="text/plain",
                    ),
                ),
            ],
        ),
    ]


def test_generator_can_create_descriptor_files(sample_resources):
    file_provider = FilesystemFileProvider()
    package_path = Path("./tests/output/test_descriptor_generator")
    file_provider.delete_dir_and_contents(package_path)

    generator = DescriptorGenerator(package_path=package_path, resources=sample_resources)
    generator.write_files()

    assert (package_path / "00000000-0000-0000-0000-000000000001" / "descriptor" /
            "00000000-0000-0000-0000-000000000001.monograph.mets2.xml").exists()
    assert (package_path / "00000000-0000-0000-0000-000000001001" / "descriptor" /
            "00000000-0000-0000-0000-000000001001.file_set.mets2.xml").exists()


def test_generator_can_return_entries(sample_resources):
    file_provider = FilesystemFileProvider()
    package_path = Path("./tests/output/test_descriptor_generator")
    file_provider.delete_dir_and_contents(package_path)

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
