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
            alternate_identifier=AlternateIdentifier(id="xyzzy:00000001", type="DLXS"),
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
                    use="DESCRIPTIVE/COMMON",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.common.json",
                        mdtype="DOR:SCHEMA",
                        mimetype="application/json",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000000102",
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

        resource = ResourceProvider(self.file_provider, self.root_resource_path).get_resource()
        self.assertEqual(expected_resource, resource)

    def test_resource_provider_provides_file_set_resource(self):
        expected_resource = PackageResource(
            id=uuid.UUID("00000000-0000-0000-0000-000000001001"),
            type="File Set",
            alternate_identifier=AlternateIdentifier(
                id="xyzzy:00000001:00000001", type="DLXS"
            ),
            events=[
                PreservationEvent(
                    identifier="e88b7591-31db-4e32-98dc-b35f94c662cd",
                    type="generate access derivative",
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
                    use="TECHNICAL",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.source.jpg.mix.xml",
                        mdtype="NISOIMG",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000100102",
                    use="TECHNICAL",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.access.jpg.mix.xml",
                        mdtype="NISOIMG",
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
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000100104",
                    use="TECHNICAL",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.plaintext.txt.textmd.xml",
                        mdtype="TEXTMD",
                    ),
                ),
                FileMetadata(
                    id="_00000000-0000-0000-0000-000000100105",
                    use="EVENT",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/metadata/00000001.plaintext.txt.premis.event.xml",
                        mdtype="PREMIS",
                    ),
                ),
            ],
            data_files=[
                FileMetadata(
                    id="_be653ff450ae7f3520312a53e56c00bc",
                    mdid="_00000000-0000-0000-0000-000000100101",
                    use="SOURCE",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/data/00000001.source.jpg",
                        mimetype="image/jpeg",
                    ),
                ),
                FileMetadata(
                    id="_7e923d9c33b3859e1327fa53a8e609a1",
                    groupid="_be653ff450ae7f3520312a53e56c00bc",
                    mdid="_00000000-0000-0000-0000-000000100102",
                    use="ACCESS",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/data/00000001.access.jpg",
                        mimetype="image/jpeg",
                    ),
                ),
                FileMetadata(
                    id="_764ba9761fbc6cbf0462d28d19356148",
                    groupid="_be653ff450ae7f3520312a53e56c00bc",
                    mdid="_00000000-0000-0000-0000-000000100104",
                    use="SOURCE",
                    ref=FileReference(
                        locref="00000000-0000-0000-0000-000000001001/data/00000001.plaintext.txt",
                        mimetype="text/plain",
                    ),
                ),
            ],
        )

        resource = ResourceProvider(self.file_provider, self.file_set_resource_path).get_resource()
        self.assertEqual(expected_resource, resource)
