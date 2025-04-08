from datetime import UTC, datetime

from dor.providers.serializers import PreservationEventSerializer
from dor.providers.models import Agent, PreservationEvent


def test_preservation_event_serializer_creates_xml_data():
    event = PreservationEvent(
        identifier="12de70c6-09aa-43e6-9f75-72d90559e8ba",
        type="generate service derivative",
        datetime=datetime(2025, 4, 8, 12, 0, 0, tzinfo=UTC),
        detail="More details go here.",
        agent=Agent(
            address="example@org.edu",
            role="image_processing"
        )
    )
    serializer = PreservationEventSerializer(event)
    data = serializer.serialize()
    expected_data = """
<PREMIS:premis xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:PREMIS="http://www.loc.gov/premis/v3" xsi:schemaLocation="http://www.loc.gov/premis/v3 http://www.loc.gov/standards/premis/v3/premis.xsd" version="3.0">
  <PREMIS:event>
    <PREMIS:eventIdentifier>
      <PREMIS:eventIdentifierType>UUID</PREMIS:eventIdentifierType>
      <PREMIS:eventIdentifierValue>12de70c6-09aa-43e6-9f75-72d90559e8ba</PREMIS:eventIdentifierValue>
    </PREMIS:eventIdentifier>
    <PREMIS:eventType>generate service derivative</PREMIS:eventType>
    <PREMIS:eventDateTime>2025-04-08T12:00:00Z</PREMIS:eventDateTime>
    <PREMIS:eventDetailInformation>
      <PREMIS:eventDetail>More details go here.</PREMIS:eventDetail>
    </PREMIS:eventDetailInformation>
    <PREMIS:linkingAgentIdentifier>
      <PREMIS:linkingAgentIdentifierType>image_processing</PREMIS:linkingAgentIdentifierType>
      <PREMIS:linkingAgentIdentifierValue>example@org.edu</PREMIS:linkingAgentIdentifierValue>
    </PREMIS:linkingAgentIdentifier>
  </PREMIS:event>
</PREMIS:premis>
    """.strip()
    assert expected_data == data


