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
            / "00000000-0000-0000-0000-000000000001.premis.event.xml"
        )

    def test_parser_can_get_preservation_event(self):
        expected_event = PreservationEvent(
            identifier="f5383b6a-c41c-4423-8288-8a4889ed8a48",
            type="ingest",
            datetime=datetime(2018, 5, 17, 14, 12, 54, tzinfo=UTC),
            detail="Giardino si bisogno.",
            agent=Agent(
                address="pierina28@example.org",
                role="collection manager",
            ),
        )
        event = PreservationEventFileParser(self.preservation_event_file_path).get_event()
        self.assertEqual(expected_event, event)
