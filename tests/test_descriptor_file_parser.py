from pathlib import Path
from unittest import TestCase
import uuid

from dor.providers.parsers import DescriptorFileParser
from dor.providers.models import (
    AlternateIdentifier,
    FileMetadata,
    FileReference,
    StructMap,
    StructMapItem,
    StructMapType,
)


class DescriptorFileParserTest(TestCase):

    def setUp(self):
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
        parser = DescriptorFileParser(self.descriptor_path)
        self.assertEqual(
            parser.get_id(), uuid.UUID("00000000-0000-0000-0000-000000000001")
        )

    def test_parser_can_get_type(self):
        parser = DescriptorFileParser(self.descriptor_path)
        self.assertEqual(parser.get_type(), "Monograph")

    def test_parser_can_get_root(self):
        parser = DescriptorFileParser(self.descriptor_path)
        self.assertEqual(parser.get_root(), True)

    def test_parser_can_get_alternate_identifier(self):
        parser = DescriptorFileParser(self.descriptor_path)

        expected_identifier = AlternateIdentifier(type="DLXS", id="xyzzy:00000001")

        self.assertEqual(parser.get_alternate_identifier(), expected_identifier)

    def test_parser_can_get_preservation_event_paths(self):
        parser = DescriptorFileParser(self.descriptor_path)
        pres_event_paths = parser.get_preservation_event_paths()
        self.assertSetEqual(set([
            "00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.premis.event.xml",
        ]), set(pres_event_paths))

    def test_parser_can_get_metadata_files(self):

        parser = DescriptorFileParser(self.descriptor_path)
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
                use="EVENT",
                ref=FileReference(
                    locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.premis.event.xml",
                    mdtype="PREMIS",
                    mimetype="text/xml",
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
                        file_set_id="urn:dor:00000000-0000-0000-0000-000000001001",
                    ),
                    StructMapItem(
                        order=2,
                        type="page",
                        label="Page 2",
                        file_set_id="urn:dor:00000000-0000-0000-0000-000000001002",
                    ),
                ],
            )
        ]

        self.assertEqual(parser.get_struct_maps(), expected_struct_maps)
