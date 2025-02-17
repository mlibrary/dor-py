from pathlib import Path
from unittest import TestCase
from datetime import datetime, UTC
import uuid

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.parsers import DescriptorFileParser
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


class DescriptorFileParserTest(TestCase):

    def setUp(self):
        self.file_provider = FilesystemFileProvider()
        self.test_submission_path = Path("tests/fixtures/test_submission_package")
        self.descriptor_path = (
            self.test_submission_path
            / "xyzzy-00000000-0000-0000-0000-000000000001-v1"
            / "data"
            / "00000000-0000-0000-0000-000000000001"
            / "descriptor"
            / "00000000-0000-0000-0000-000000000001.monograph.mets2.xml"
        )

        self.file_set_descriptor_path = (
            self.test_submission_path
            / "xyzzy-00000000-0000-0000-0000-000000000001-v1"
            / "data"
            / "00000000-0000-0000-0000-000000001001"
            / "descriptor"
            / "00000000-0000-0000-0000-000000001001.file_set.mets2.xml"
        )

        return super().setUp()

    def test_parser_can_get_id(self):
        parser = DescriptorFileParser(self.descriptor_path, self.file_provider)
        self.assertEqual(
            parser.get_id(), uuid.UUID("00000000-0000-0000-0000-000000000001")
        )

    def test_parser_can_get_type(self):
        parser = DescriptorFileParser(self.descriptor_path, self.file_provider)
        self.assertEqual(parser.get_type(), "Monograph")

    def test_parser_can_get_alternate_identifier(self):
        parser = DescriptorFileParser(self.descriptor_path, self.file_provider)

        expected_identifier = AlternateIdentifier(type="DLXS", id="xyzzy:00000001")

        self.assertEqual(parser.get_alternate_identifier(), expected_identifier)

    def test_parser_can_get_preservation_events(self):
        expected_events = [
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
        ]

        parser = DescriptorFileParser(self.descriptor_path, self.file_provider)
        self.assertEqual(parser.get_preservation_events(), expected_events)

    def test_parser_can_get_metadata_files(self):

        parser = DescriptorFileParser(self.descriptor_path, self.file_provider)
        expected_file_metadata = [
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
                use="PROVENANCE",
                ref=FileReference(
                    locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.premis.event.xml",
                    mdtype="PREMIS",
                    mimetype="text/xml",
                ),
            ),
        ]

        self.assertEqual(parser.get_metadata_files(), expected_file_metadata)

    def test_parser_can_get_struct_maps(self):

        parser = DescriptorFileParser(self.descriptor_path, self.file_provider)
        expected_struct_maps = [
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
        ]

        self.assertEqual(parser.get_struct_maps(), expected_struct_maps)

    def test_parser_can_parse_monograph(self):

        expected_resource = PackageResource(
            id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            type="Monograph",
            alternate_identifier=AlternateIdentifier(id="xyzzy:00000001", type="DLXS"),
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
                    use="PROVENANCE",
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

        parser = DescriptorFileParser(self.descriptor_path, self.file_provider)
        self.assertEqual(parser.get_resource(), expected_resource)

    def test_parser_can_parse_file_set(self):
        parser = DescriptorFileParser(self.file_set_descriptor_path, self.file_provider)

        expected_resource = PackageResource(
            id=uuid.UUID("00000000-0000-0000-0000-000000001001"),
            type="File Set",
            alternate_identifier=AlternateIdentifier(
                id="xyzzy:00000001:00000001", type="DLXS"
            ),
            events=[
                PreservationEvent(
                    identifier="f9fa8a15-7be0-4ad5-8682-4423793c9f1d",
                    type="generate access derivative",
                    datetime=datetime(1973, 5, 23, 21, 42, 15, tzinfo=UTC),
                    detail="Care instead also much.",
                    agent=Agent(
                        address="sweaver@example.com",
                        role="image processing",
                    ),
                ),
                PreservationEvent(
                    identifier="006c79ed-f63e-466f-b1fb-171cc229b901",
                    type="extract text",
                    datetime=datetime(1998, 8, 29, 13, 3, 58, tzinfo=UTC),
                    detail="Human debate million theory capital.",
                    agent=Agent(
                        address="moorenicholas@example.com",
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
                    use="PROVENANCE",
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
                    use="PROVENANCE",
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

        self.assertEqual(parser.get_resource(), expected_resource)
