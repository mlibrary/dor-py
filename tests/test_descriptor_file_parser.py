from pathlib import Path
from unittest import TestCase
from datetime import datetime, UTC
import uuid

from dor.providers.parsers import *
from dor.providers.models import *


class DescriptorFileParserTest(TestCase):

    def setUp(self):
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
        parser = DescriptorFileParser(self.descriptor_path)
        self.assertEqual(parser.get_id(), uuid.UUID("00000000-0000-0000-0000-000000000001"))

    def test_parser_can_get_type(self):
        parser = DescriptorFileParser(self.descriptor_path)
        self.assertEqual(
            parser.get_type(), "Monograph"
        )

    def test_parser_can_get_alternate_identifier(self):
        parser = DescriptorFileParser(self.descriptor_path)

        expected_identifier = AlternateIdentifier(type="DLXS", id="xyzzy:00000001")

        self.assertEqual(parser.get_alternate_identifier(), expected_identifier)

    def test_parser_can_get_preservation_events(self):
        expected_events = [
            PreservationEvent(
                identifier="e01727d0-b4d9-47a5-925a-4018f9cac6b8",
                type="ingest",
                datetime=datetime(1983, 5, 17, 11, 9, 45, tzinfo=UTC),
                detail="Girl voice lot another blue nearly.",
                agent=Agent(address="matthew24@example.net", role="collection manager"),
            )
        ]

        parser = DescriptorFileParser(self.descriptor_path)
        self.assertEqual(parser.get_preservation_events(), expected_events)

    def test_parser_can_get_metadata_files(self):

        parser = DescriptorFileParser(self.descriptor_path)
        expected_file_metadata = [
            FileMetadata(
                id="_0193972b-e591-7e28-b8cb-1babed52f606",
                use="DESCRIPTIVE/COMMON",
                ref=FileReference(
                    locref="../metadata/00000000-0000-0000-0000-000000000001.common.json",
                    mdtype="DOR:SCHEMA",
                    mimetype="application/json",
                ),
            ),
            FileMetadata(
                id="_0193972b-e592-7647-8e51-10db514433f7",
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
        ]

        self.assertEqual(parser.get_metadata_files(), expected_file_metadata)

    def test_parser_can_get_struct_maps(self):

        parser = DescriptorFileParser(self.descriptor_path)
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
                    identifier="e01727d0-b4d9-47a5-925a-4018f9cac6b8",
                    type="ingest",
                    datetime=datetime(1983, 5, 17, 11, 9, 45, tzinfo=UTC),
                    detail="Girl voice lot another blue nearly.",
                    agent=Agent(
                        address="matthew24@example.net", role="collection manager"
                    ),
                )
            ],
            metadata_files=[
                FileMetadata(
                    id="_0193972b-e591-7e28-b8cb-1babed52f606",
                    use="DESCRIPTIVE/COMMON",
                    ref=FileReference(
                        locref="../metadata/00000000-0000-0000-0000-000000000001.common.json",
                        mdtype="DOR:SCHEMA",
                        mimetype="application/json",
                    ),
                ),
                FileMetadata(
                    id="_0193972b-e592-7647-8e51-10db514433f7",
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

        parser = DescriptorFileParser(self.descriptor_path)
        self.assertEqual(parser.get_resource(), expected_resource)

    def test_parser_can_parse_asset(self):
        descriptor_path = ( 
            self.descriptor_path 
            / ".." 
            / "00000000-0000-0000-0000-000000001001.asset.mets2.xml" 
        ).resolve()

        expected_resource = PackageResource(
            id=uuid.UUID("00000000-0000-0000-0000-000000001001"),
            type="Asset",
            alternate_identifier=AlternateIdentifier(
                id="xyzzy:00000001:00000001", type="DLXS"
            ),
            events=[
                PreservationEvent(
                    identifier="81388465-aefd-4a3d-ba99-a868d062b92e",
                    type="generate access derivative",
                    datetime=datetime(2005, 8, 22, 22, 54, 45, tzinfo=UTC),
                    detail="Method south agree until.",
                    agent=Agent(address="rguzman@example.net", role="image processing"),
                ),
                PreservationEvent(
                    identifier="d53540b9-cd23-4e92-9dff-4b28bf050b26",
                    type="extract text",
                    datetime=datetime(2006, 8, 23, 16, 21, 57, tzinfo=UTC),
                    detail="Hear thus part probably that.",
                    agent=Agent(address="kurt16@example.org", role="ocr processing"),
                ),
            ],
            metadata_files=[
                FileMetadata(
                    id="_0193972b-e4a4-7985-abe2-f3f1259b78ec",
                    use="TECHNICAL",
                    ref=FileReference(
                        locref="../metadata/00000001.source.jpg.mix.xml",
                        mdtype="NISOIMG",
                    ),
                ),
                FileMetadata(
                    id="_0193972b-e4ae-73eb-848d-5f8893b68253",
                    use="TECHNICAL",
                    ref=FileReference(
                        locref="../metadata/00000001.access.jpg.mix.xml",
                        mdtype="NISOIMG",
                    ),
                ),
                FileMetadata(
                    id="_0193972b-e572-7107-b69c-e2f4c660a9aa",
                    use="TECHNICAL",
                    ref=FileReference(
                        locref="../metadata/00000001.plaintext.txt.textmd.xml",
                        mdtype="TEXTMD",
                    ),
                ),
            ],
            data_files=[
                FileMetadata(
                    id="_be653ff450ae7f3520312a53e56c00bc",
                    mdid="_0193972b-e4a4-7985-abe2-f3f1259b78ec",
                    use="SOURCE",
                    ref=FileReference(
                        locref="../data/00000001.source.jpg",
                        mimetype="image/jpeg",
                    ),
                ),
                FileMetadata(
                    id="_7e923d9c33b3859e1327fa53a8e609a1",
                    groupid="_be653ff450ae7f3520312a53e56c00bc",
                    mdid="_0193972b-e4ae-73eb-848d-5f8893b68253",
                    use="ACCESS",
                    ref=FileReference(
                        locref="../data/00000001.access.jpg",
                        mimetype="image/jpeg",
                    ),
                ),
                FileMetadata(
                    id="_764ba9761fbc6cbf0462d28d19356148",
                    groupid="_be653ff450ae7f3520312a53e56c00bc",
                    mdid="_0193972b-e572-7107-b69c-e2f4c660a9aa",
                    use="SOURCE",
                    ref=FileReference(
                        locref="../data/00000001.plaintext.txt",
                        mimetype="text/plain",
                    ),
                ),
            ],
        )

        parser = DescriptorFileParser(descriptor_path)
        self.assertEqual(parser.get_resource(), expected_resource)
