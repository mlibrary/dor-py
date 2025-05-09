import uuid
from datetime import datetime, UTC
from pathlib import Path
from unittest import TestCase

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
from dor.providers.resource_provider import ResourceProvider


class ResourceProviderTest(TestCase):

    def setUp(self):
        self.file_provider = FilesystemFileProvider()
        self.test_submission_path = Path("tests/fixtures/test_submission_package")

        self.root_resource_path = (
            self.test_submission_path
            / "xyzzy-00000000-0000-0000-0000-000000000001-v1"
            / "data"
            / "00000000-0000-0000-0000-000000000001"
        )

        self.file_set_resource_path = (
            self.test_submission_path
            / "xyzzy-00000000-0000-0000-0000-000000000001-v1"
            / "data"
            / "00000000-0000-0000-0000-000000001001"
        )

        return super().setUp()

    def test_resource_provider_provides_root_resource(self):
        expected_resource = PackageResource(
            id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            type="Monograph",
            root=True,
            alternate_identifier=[AlternateIdentifier(id="xyzzy:00000001", type="DLXS")],
            events=[
                PreservationEvent(
                    identifier="8c1e311a-e477-409f-aed3-d0ddbcfbc3fa",
                    type="ingest",
                    datetime=datetime(2007, 7, 9, 16, 19, 24, tzinfo=UTC),
                    detail="Ball change find heart.",
                    agent=Agent(
                        address="dunnhannah@example.com",
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

        resource = ResourceProvider(self.file_provider, self.root_resource_path).get_resource()
        self.assertEqual(expected_resource, resource)

    def test_resource_provider_provides_file_set_resource(self):
        expected_resource = PackageResource(
            id=uuid.UUID("00000000-0000-0000-0000-000000001001"),
            type="File Set",
            alternate_identifier=[AlternateIdentifier(
                id="xyzzy:00000001:00000001", type="DLXS"
            )],
            events=[
                PreservationEvent(
                    identifier="e88b7591-31db-4e32-98dc-b35f94c662cd",
                    type="generate service derivative",
                    datetime=datetime(2026, 9, 18, 9, 40, 58, tzinfo=UTC),
                    detail="Level professional Democrat develop eye realize.",
                    agent=Agent(
                        address="markkim@example.com",
                        role="image processing",
                    ),
                ),
                PreservationEvent(
                    identifier="e3bb0157-f9a0-47d6-b24c-44878c1e311a",
                    type="extract text",
                    datetime=datetime(2026, 11, 4, 3, 52, 43, tzinfo=UTC),
                    detail="Whatever this front attack.",
                    agent=Agent(
                        address="steven34@example.net",
                        role="ocr processing",
                    ),
                ),
            ],
            metadata_files=[
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000100101",
                    use="function:technical",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.function:source.format:image.jpg.function:technical.mix.xml",
                        mdtype="NISOIMG",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000100102",
                    use="function:technical",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.function:service.format:image.jpg.function:technical.mix.xml",
                        mdtype="NISOIMG",
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
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000100104",
                    use="function:technical",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.function:service.format:text-plain.txt.function:technical.textmd.xml",
                        mdtype="TEXTMD",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000100105",
                    use="function:event",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.function:service.format:text-plain.txt.function:event.premis.xml",
                        mdtype="PREMIS",
                    ),
                ),
            ],
            data_files=[
                FileMetadata(
                    id="_36f8b6397d7defc7b0477671e7f1c562",
                    mdid="_00000000-0000-0000-0000-000000100101",
                    use="function:source format:image",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/data/00000001.function:source.format:image.jpg",
                        mimetype="image/jpeg",
                    ),
                ),
                FileMetadata(
                    id="_79edd2750da9507bdfb0682d10bda694",
                    groupid="_36f8b6397d7defc7b0477671e7f1c562",
                    mdid="_00000000-0000-0000-0000-000000100102",
                    use="function:service format:image",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/data/00000001.function:service.format:image.jpg",
                        mimetype="image/jpeg",
                    ),
                ),
                FileMetadata(
                    id="_f235434ccd54adabca960b775f54449e",
                    groupid="_36f8b6397d7defc7b0477671e7f1c562",
                    mdid="_00000000-0000-0000-0000-000000100104",
                    use="function:service format:text-plain",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/data/00000001.function:service.format:text-plain.txt",
                        mimetype="text/plain",
                    ),
                ),
            ],
        )

        resource = ResourceProvider(self.file_provider, self.file_set_resource_path).get_resource()
        self.assertEqual(expected_resource, resource)
