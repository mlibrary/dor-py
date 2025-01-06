from datetime import datetime
import os
from typing import Optional
import uuid
from pathlib import Path

from utils.element_adapter import ElementAdapter
from .models import Agent, AlternateIdentifier, FileMetadata, FileReference, PackageResource, PreservationEvent, StructMap, StructMapItem, StructMapType


class DescriptorFileParser:
    namespaces: dict[str, str] = {
        "METS": "http://www.loc.gov/METS/v2",
        "PREMIS": "http://www.loc.gov/premis/v3",
    }

    def __init__(self, element_adapter: ElementAdapter, descriptor_path: Path):
        self.tree: ElementAdapter = element_adapter
        self.descriptor_path = descriptor_path

    def get_id(self):
        return uuid.UUID(self.tree.get("OBJID"))

    def get_type(self):
        hdr = self.tree.find("METS:metsHdr")
        return hdr.get("TYPE")

    def get_alternate_identifier(self)-> AlternateIdentifier:
        alt_record_id = self.tree.find("METS:metsHdr/METS:altRecordID")
        if alt_record_id:
            return AlternateIdentifier(
                type=alt_record_id.get("TYPE"), id=alt_record_id.text
            )
        return AlternateIdentifier(type="", id="")    

    def get_preservation_events(self) -> list[PreservationEvent]:
        return [self.get_event(elem) for elem in self.tree.findall(".//PREMIS:event")]

    def get_event(self, elem: ElementAdapter) -> PreservationEvent:
        event_identifier = elem.find(".//PREMIS:eventIdentifierValue").text
        event_type = elem.find(".//PREMIS:eventType").text
        event_datetime = elem.find(".//PREMIS:eventDateTime").text
        event_detail = elem.find(".//PREMIS:eventDetail").text
        agent_role = elem.find(".//PREMIS:linkingAgentIdentifierType").text
        agent_address = elem.find(".//PREMIS:linkingAgentIdentifierValue").text
        return PreservationEvent(
            identifier=event_identifier,
            type=event_type,
            datetime=datetime.fromisoformat(event_datetime),
            detail=event_detail,
            agent=Agent(address=agent_address, role=agent_role),
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

    def get_md_file_metadatum(self, elem: ElementAdapter):
        id_ = elem.get("ID")
        use = elem.get("USE")
        md_red_element = elem.find("METS:mdRef")
        locref: Optional[str] = None
        mdtype: Optional[str] = None
        mimetype: Optional[str] = None 
        if md_red_element:
            locref = self._apply_relative_path(self.descriptor_path, md_red_element.get_optional("LOCREF"))
            mdtype = md_red_element.get_optional("MDTYPE")
            mimetype = md_red_element.get_optional("MIMETYPE", None)

        return FileMetadata(
            id=id_,
            use=use,
            ref=FileReference(locref=str(locref), mdtype=mdtype, mimetype=mimetype),
        )

    def get_filesec_file_metadatum(self, elem: ElementAdapter):
        id_ = elem.get("ID")
        use = elem.get("USE")
        mdid = elem.get_optional("MDID", None)
        groupid = elem.get_optional("GROUPID", None)
        mimetype = elem.get_optional('MIMETYPE', None)
        mdtype = None
        flocat_element = elem.find("METS:FLocat")
        locref: Optional[str] = None
        
        if flocat_element:
            locref = self._apply_relative_path(self.descriptor_path, flocat_element.get_optional("LOCREF"))

        return FileMetadata(
            id=id_,
            use=use,
            mdid=mdid,
            groupid=groupid,
            ref=FileReference(locref=str(locref), mdtype=mdtype, mimetype=mimetype),
        )

    def get_struct_maps(self)-> list[StructMap]:
        struct_maps: list[StructMap] = []
        for struct_map_elem in self.tree.findall(".//METS:structMap"):
            struct_map_id = struct_map_elem.get("ID")
            struct_map_type = struct_map_elem.get("TYPE")

            order_elems = struct_map_elem.findall(".//METS:div[@ORDER]")

            struct_map_items: list[StructMapItem] = []
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
        
    def _apply_relative_path(self, descriptor_path: Path, path_to_apply: str) -> str:
        resolved_combined_path = path_to_apply
        if path_to_apply.startswith("../"):
            combined_path = os.path.join(descriptor_path, path_to_apply) 
            resolved_combined_path = str(os.path.normpath(combined_path))
        return resolved_combined_path    