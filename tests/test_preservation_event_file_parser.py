from datetime import datetime, UTC
from pathlib import Path
from unittest import TestCase

from dor.providers.models import Agent, PreservationEvent
from dor.providers.parsers import PreservationEventFileParser


class PreservationEventFileParserTest(TestCase):

    def setUp(self):
        self.test_submission_path = Path("tests/fixtures/test_submission_package")
        self.preservation_event_file_path = (
            self.test_submission_path
            / "xyzzy-00000000-0000-0000-0000-000000000001-v1"
            / "data"
            / "00000000-0000-0000-0000-000000000001"
            / "metadata"
            / "00000000-0000-0000-0000-000000000001.function:event.premis.xml"
        )

    def test_parser_can_get_preservation_event(self):
        expected_event = PreservationEvent(
            identifier="8c1e311a-e477-409f-aed3-d0ddbcfbc3fa",
            type="ingest",
            datetime=datetime(2007, 7, 9, 16, 19, 24, tzinfo=UTC),
            detail="Ball change find heart.",
            agent=Agent(
                address="dunnhannah@example.com",
                role="collection manager",
            ),
        )
        event = PreservationEventFileParser(self.preservation_event_file_path).get_event()
        self.assertEqual(expected_event, event)
