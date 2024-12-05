from datetime import datetime
import uuid

from utils.element_adapter import ElementAdapter
from .models import *


class DescriptorFileParser:
    namespaces: dict[str, str] = {
        "METS": "http://www.loc.gov/METS/v2",
        "PREMIS": "http://www.loc.gov/premis/v3",
    }

    def __init__(self, descriptor_path):
        try:
            text = descriptor_path.read_text()
        except FileNotFoundError as e:
            raise FileNotFoundError from e
        self.tree: ElementAdapter = ElementAdapter.from_string(text, self.namespaces)

    def get_id(self):
        return uuid.UUID(self.tree.get("OBJID"))

    def get_type(self):
        hdr = self.tree.find("METS:metsHdr")
        return hdr.get("TYPE")

    def get_alternate_identifier(self):
        alt_record_id = self.tree.find("METS:metsHdr/METS:altRecordID")
        if alt_record_id:
            return AlternateIdentifier(
                type=alt_record_id.get("TYPE"), id=alt_record_id.text
            )

    def get_preservation_events(self) -> list[PreservationEvent]:
        return [self.get_event(elem) for elem in self.tree.findall(".//PREMIS:event")]

    def get_event(self, elem) -> PreservationEvent:
        event_identifier = elem.find(".//PREMIS:eventIdentifierValue").text
        event_type = elem.find(".//PREMIS:eventType").text
        event_datetime = elem.find(".//PREMIS:eventDateTime").text
        event_detail = elem.find(".//PREMIS:eventDetail").text
        actor_role = elem.find(".//PREMIS:linkingAgentIdentifierType").text
        actor_address = elem.find(".//PREMIS:linkingAgentIdentifierValue").text
        return PreservationEvent(
            identifier=event_identifier,
            type=event_type,
            datetime=datetime.fromisoformat(event_datetime),
            detail=event_detail,
            agent=Agent(address=actor_address, role=actor_role),
        )

    def get_file_metadata(self) -> list[FileMetadata]:
        # return [
        #     self.get_file_metadatum(elem)
        #     for elem in self.tree.findall(".//METS:md[@USE != 'PROVENANCE' and @USE != 'COLLECTIONS']")
        # ]
        results = []
        for elem in self.tree.findall(".//METS:md"):
            if elem.get("USE") in ["COLLECTIONS", "PROVENANCE"]:
                continue
            results.append(self.get_file_metadatum(elem))
        return results

    def get_file_metadatum(self, elem):
        id_ = elem.get("ID")
        use = elem.get("USE")
        locref = elem.find("METS:mdRef").get_optional("LOCREF")
        mdtype = elem.find("METS:mdRef").get_optional("MDTYPE")
        mimetype = elem.find("METS:mdRef").get_optional("MIMETYPE")

        return FileMetadata(
            id=id_,
            use=use,
            ref=FileReference(locref=locref, mdtype=mdtype, mimetype=mimetype),
        )

    def get_member_ids(self):
        divs = self.tree.findall(
            ".//METS:structMap[@TYPE='physical']/METS:div/METS:div"
        )
        return [elem.get("ID").replace("urn:dor:", "") for elem in divs]

    def get_resource(self):
        return PackageResource(
            id=self.get_id(),
            alternate_identifier=self.get_alternate_identifier(),
            type=self.get_type(),
            events=self.get_preservation_events(),
            file_metadata=self.get_file_metadata(),
            member_ids=self.get_member_ids(),
        )
