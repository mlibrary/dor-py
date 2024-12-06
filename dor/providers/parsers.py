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
        text = descriptor_path.read_text()
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

    def get_metadata_files(self) -> list[FileMetadata]:
        return [
            self.get_md_file_metadatum(elem)
            for elem in self.tree.findall(".//METS:md[METS:mdRef]")
        ]

    def get_data_files(self) -> list[FileMetadata]:
        return [
            self.get_filesec_file_metadatum(elem)
            for elem in self.tree.findall(".//METS:file")
        ]

    def get_md_file_metadatum(self, elem):
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

    def get_filesec_file_metadatum(self, elem):
        id_ = elem.get("ID")
        use = elem.get("USE")
        mdid = elem.get_optional("MDID", None)
        groupid = elem.get_optional("GROUPID", None)
        mimetype = elem.get('MIMETYPE')
        mdtype = None
        locref = elem.find("METS:FLocat").get_optional("LOCREF")

        return FileMetadata(
            id=id_,
            use=use,
            mdid=mdid,
            groupid=groupid,
            ref=FileReference(locref=locref, mdtype=mdtype, mimetype=mimetype),
        )

    def get_struct_maps(self):
        struct_maps = []
        for struct_map_elem in self.tree.findall(".//METS:structMap"):
            struct_map_id = struct_map_elem.get("ID")
            struct_map_type = struct_map_elem.get("TYPE")

            order_elems = struct_map_elem.findall(".//METS:div[@ORDER]")

            struct_map_items = []
            for order_elem in order_elems:
                order_number = int(order_elem.get("ORDER"))
                label = order_elem.get("LABEL")
                asset_id = order_elem.get("ID")
                order_elem_type = order_elem.get_optional("TYPE", None)
                struct_map_items.append(StructMapItem(
                    order=order_number,
                    label=label,
                    asset_id=asset_id,
                    type=order_elem_type,
                ))

            struct_maps.append(
                StructMap(
                    id=struct_map_id,
                    type=StructMapType[struct_map_type.upper()],
                    items=struct_map_items,
                )
            )

        return struct_maps

    def get_resource(self):
        return PackageResource(
            id=self.get_id(),
            alternate_identifier=self.get_alternate_identifier(),
            type=self.get_type(),
            events=self.get_preservation_events(),
            metadata_files=self.get_metadata_files(),
            data_files=self.get_data_files(),
            struct_maps=self.get_struct_maps(),
        )
