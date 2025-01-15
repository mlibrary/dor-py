from pathlib import Path
from unittest import TestCase
from datetime import datetime, UTC
import uuid
import pytest

from dor.providers.file_system_file_provider import FilesystemHandler
from dor.providers.parsers import DescriptorFileParser
from dor.providers.models import (
    Agent, AlternateIdentifier, FileMetadata, FileReference, PackageResource,
    PreservationEvent, StructMap, StructMapItem, StructMapType
)

class DescriptorFileParserTest(TestCase):
    
    def setUp(self):
        self.file_provider = FilesystemHandler()
        self.test_submission_path = Path("tests/fixtures/test_submission_package")
        self.descriptor_path = (
            self.test_submission_path
            / "xyzzy-0001-v1"
            / "data"
            / "00000000-0000-0000-0000-000000000001"
            / "descriptor"
            / "00000000-0000-0000-0000-000000000001.monograph.mets2.xml"
        )
        return super().setUp()

    def test_parser_can_get_id(self):
        parser = DescriptorFileParser(self.descriptor_path, self.file_provider)
        self.assertEqual(parser.get_id(), uuid.UUID("00000000-0000-0000-0000-000000000001"))

    def test_parser_can_get_type(self):
        parser = DescriptorFileParser(self.descriptor_path, self.file_provider)
        self.assertEqual(
            parser.get_type(), "Monograph"
        )

    def test_parser_can_get_alternate_identifier(self):
        parser = DescriptorFileParser(self.descriptor_path, self.file_provider)
        
        expected_identifier = AlternateIdentifier(type="DLXS", id="xyzzy:00000001")

        self.assertEqual(parser.get_alternate_identifier(), expected_identifier)

    def test_parser_can_get_preservation_events(self):
        expected_events = [
            PreservationEvent(
                identifier="abdcb901-721a-4be0-a981-14f514236633",
                type="ingest",
                datetime=datetime(2016, 11, 29, 13, 51, 14, tzinfo=UTC),
                detail="Middle president push visit information feel most.",
                agent=Agent(
                    address="christopherpayne@example.org", role="collection manager"
                ),
            )
        ]

        parser = DescriptorFileParser(self.descriptor_path, self.file_provider)
        self.assertEqual(parser.get_preservation_events(), expected_events)

    def test_parser_can_get_metadata_files(self):

        parser = DescriptorFileParser(self.descriptor_path, self.file_provider)
        expected_file_metadata = [
            FileMetadata(
                id="_0193d5f0-7f64-7ac8-8f94-85c55c7313e4",
                use="DESCRIPTIVE/COMMON",
                ref=FileReference(
                    locref="tests/fixtures/test_submission_package/xyzzy-0001-v1/data/00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.common.json",
                    mdtype="DOR:SCHEMA",
                    mimetype="application/json",
                ),
            ),
            FileMetadata(
                id="_0193d5f0-7f65-783e-b7b4-485b6f6b24d0",
                use="DESCRIPTIVE",
                ref=FileReference(
                    locref="tests/fixtures/test_submission_package/xyzzy-0001-v1/data/00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.metadata.json",
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
                        locref="tests/fixtures/test_submission_package/xyzzy-0001-v1/data/00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.common.json",
                        mdtype="DOR:SCHEMA",
                        mimetype="application/json",
                    ),
                ),
                FileMetadata(
                    id="_0193d5f0-7f65-783e-b7b4-485b6f6b24d0",
                    use="DESCRIPTIVE",
                    ref=FileReference(
                        locref="tests/fixtures/test_submission_package/xyzzy-0001-v1/data/00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.metadata.json",
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

        parser = DescriptorFileParser(self.descriptor_path, self.file_provider)
        self.assertEqual(parser.get_resource(), expected_resource)

    def test_parser_can_parse_asset(self):
        parser = DescriptorFileParser(self.descriptor_path, self.file_provider)
        descriptor_file_path = parser.file_provider.apply_relative_path( 
            self.descriptor_path, 
            "../00000000-0000-0000-0000-000000001001.asset.mets2.xml" 
        )

        expected_resource = PackageResource(
            id=uuid.UUID("00000000-0000-0000-0000-000000001001"),
            type="Asset",
            alternate_identifier=AlternateIdentifier(
                id="xyzzy:00000001:00000001", type="DLXS"
            ),
            events=[
                PreservationEvent(
                    identifier="fe4c76e5-dbf1-4934-97fb-52ef5a68f073",
                    type="generate access derivative",
                    datetime=datetime(1993, 6, 11, 4, 44, 7, tzinfo=UTC),
                    detail="Night wonder three him family structure simple.",
                    agent=Agent(address="arroyoalan@example.net", role="image processing"),
                ),
                PreservationEvent(
                    identifier="3bdcb1e3-4674-4b9c-83c8-4f9f9fe50812",
                    type="extract text",
                    datetime=datetime(1988, 5, 26, 18, 33, 46, tzinfo=UTC),
                    detail="Player center road attorney speak wait partner.",
                    agent=Agent(address="jonathanjones@example.net", role="ocr processing"),
                ),
            ],
            metadata_files=[
                FileMetadata(
                    id="_0193d5f0-7e72-7481-b6fd-0f916c30b396",
                    use="TECHNICAL",
                    ref=FileReference(
                        locref="tests/fixtures/test_submission_package/xyzzy-0001-v1/data/00000000-0000-0000-0000-000000000001/metadata/00000001.source.jpg.mix.xml",
                        mdtype="NISOIMG",
                    ),
                ),
                FileMetadata(
                    id="_0193d5f0-7e75-7803-8e41-71323b7b3284",
                    use="TECHNICAL",
                    ref=FileReference(
                        locref="tests/fixtures/test_submission_package/xyzzy-0001-v1/data/00000000-0000-0000-0000-000000000001/metadata/00000001.access.jpg.mix.xml",
                        mdtype="NISOIMG",
                    ),
                ),
                FileMetadata(
                    id="_0193d5f0-7f54-7268-b9b1-821085acdcf7",
                    use="TECHNICAL",
                    ref=FileReference(
                        locref="tests/fixtures/test_submission_package/xyzzy-0001-v1/data/00000000-0000-0000-0000-000000000001/metadata/00000001.plaintext.txt.textmd.xml",
                        mdtype="TEXTMD",
                    ),
                ),
            ],
            data_files=[
                FileMetadata(
                    id="_be653ff450ae7f3520312a53e56c00bc",
                    mdid="_0193d5f0-7e72-7481-b6fd-0f916c30b396",
                    use="SOURCE",
                    ref=FileReference(
                        locref="tests/fixtures/test_submission_package/xyzzy-0001-v1/data/00000000-0000-0000-0000-000000000001/data/00000001.source.jpg",
                        mimetype="image/jpeg",
                    ),
                ),
                FileMetadata(
                    id="_7e923d9c33b3859e1327fa53a8e609a1",
                    groupid="_be653ff450ae7f3520312a53e56c00bc",
                    mdid="_0193d5f0-7e75-7803-8e41-71323b7b3284",
                    use="ACCESS",
                    ref=FileReference(
                        locref="tests/fixtures/test_submission_package/xyzzy-0001-v1/data/00000000-0000-0000-0000-000000000001/data/00000001.access.jpg",
                        mimetype="image/jpeg",
                    ),
                ),
                FileMetadata(
                    id="_764ba9761fbc6cbf0462d28d19356148",
                    groupid="_be653ff450ae7f3520312a53e56c00bc",
                    mdid="_0193d5f0-7f54-7268-b9b1-821085acdcf7",
                    use="SOURCE",
                    ref=FileReference(
                        locref="tests/fixtures/test_submission_package/xyzzy-0001-v1/data/00000000-0000-0000-0000-000000000001/data/00000001.plaintext.txt",
                        mimetype="text/plain",
                    ),
                ),
            ],
        )

        parser = DescriptorFileParser(Path(descriptor_file_path),self.file_provider)
        self.assertEqual(parser.get_resource(), expected_resource)