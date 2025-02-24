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
                    identifier="f5383b6a-c41c-4423-8288-8a4889ed8a48",
                    type="ingest",
                    datetime=datetime(2018, 5, 17, 14, 12, 54, tzinfo=UTC),
                    detail="Giardino si bisogno.",
                    agent=Agent(
                        address="pierina28@example.org",
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
                    identifier="36eafa28-80e6-45d0-a9d9-36500c6bdf0d",
                    type="generate access derivative",
                    datetime=datetime(1999, 3, 16, 0, 4, 29, tzinfo=UTC),
                    detail="Realize defense wife audience cover become show.",
                    agent=Agent(
                        address="thomasnguyen@example.net",
                        role="image processing",
                    ),
                ),
                PreservationEvent(
                    identifier="37557161-10f8-40c1-842f-be3a386c033c",
                    type="extract text",
                    datetime=datetime(2015, 8, 8, 19, 14, 45, tzinfo=UTC),
                    detail="Cantare alcuno sorgere coprire possibile semplice.",
                    agent=Agent(
                        address="junyamada@example.net",
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
