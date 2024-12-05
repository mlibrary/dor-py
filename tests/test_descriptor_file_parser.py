from pathlib import Path
from unittest import TestCase
from datetime import datetime, UTC
import uuid

from dor.providers.parsers import *
from dor.providers.models import *


class DescriptorFileTest(TestCase):

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
        # resource = DescriptorFileParser(self.descriptor_path).parse()
        # self.assertEqual(resource.id, uuid.UUID("00000000-0000-0000-0000-000000000001"))

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

    def test_parser_can_get_file_metadata(self):

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

        self.assertEqual(parser.get_file_metadata(), expected_file_metadata)

    def test_parser_can_get_member_ids(self):

        parser = DescriptorFileParser(self.descriptor_path)
        expected_member_ids = [
            "00000000-0000-0000-0000-000000001001",
            "00000000-0000-0000-0000-000000001002"
        ]

        self.assertEqual(parser.get_member_ids(), expected_member_ids)

    def test_provider_can_parse_resource(self):

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
            file_metadata=[
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
            member_ids=[
                "00000000-0000-0000-0000-000000001001",
                "00000000-0000-0000-0000-000000001002",
            ],
        )

        parser = DescriptorFileParser(self.descriptor_path)
        self.assertEqual(parser.get_resource(), expected_resource)
