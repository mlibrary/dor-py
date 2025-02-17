from datetime import UTC, datetime
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
            / "00000000-0000-0000-0000-000000000001.premis.event.xml"
        )

    def test_parser_can_get_preservation_event(self):

        expected_event = PreservationEvent(
            identifier="23b04e8b-f7fd-4331-a3bb-0157f9a057d6",
            type="ingest",
            datetime=datetime(1974, 6, 24, 1, 8, 39, tzinfo=UTC),
            detail="This front attack nature.",
            agent=Agent(
                address="steven34@example.net",
                role="collection manager",
            ),
        )
        event = PreservationEventFileParser(self.preservation_event_file_path).get_event()
        self.assertEqual(expected_event, event)
