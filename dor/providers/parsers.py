from datetime import datetime
import uuid
from pathlib import Path

from dor.providers.file_provider import FileProvider
from utils.element_adapter import ElementAdapter
from .models import (
    Agent,
    AlternateIdentifier,
    FileMetadata,
    FileReference,
    PackageResource,
    PreservationEvent,
    StructMap,
    StructMapItem,
    StructMapType,
)


class DescriptorFileParser:
    namespaces: dict[str, str] = {
        "METS": "http://www.loc.gov/METS/v2",
        "PREMIS": "http://www.loc.gov/premis/v3",
    }

    def __init__(self, descriptor_file_path: Path, file_provider: FileProvider):
        text = descriptor_file_path.read_text()
        self.tree: ElementAdapter = ElementAdapter.from_string(text, self.namespaces)
        self.file_provider = file_provider
        self.descriptor_path: Path = file_provider.get_descriptor_dir(
            descriptor_file_path
        )

    def get_id(self):
        return uuid.UUID(self.tree.get("OBJID"))

    def get_type(self):
        hdr = self.tree.find("METS:metsHdr")
        return hdr.get("TYPE")

    def get_alternate_identifier(self) -> AlternateIdentifier:
        alt_record_id = self.tree.find("METS:metsHdr/METS:altRecordID")
        return AlternateIdentifier(
            type=alt_record_id.get("TYPE"), id=alt_record_id.text
        )

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
        md_ref_element = elem.find("METS:mdRef")
        locref = md_ref_element.get("LOCREF")
        if not locref.startswith("https"):
            locref = self.file_provider.apply_relative_path(
                self.descriptor_path, locref
            )
        mdtype = md_ref_element.get_optional("MDTYPE")
        mimetype = md_ref_element.get_optional("MIMETYPE")

        return FileMetadata(
            id=id_,
            use=use,
            ref=FileReference(locref=str(locref), mdtype=mdtype, mimetype=mimetype),
        )

    def get_filesec_file_metadatum(self, elem: ElementAdapter):
        id_ = elem.get("ID")
        use = elem.get("USE")
        mdid = elem.get_optional("MDID")
        groupid = elem.get_optional("GROUPID")
        mimetype = elem.get_optional("MIMETYPE")
        mdtype = None
        flocat_element = elem.find("METS:FLocat")
        locref = flocat_element.get("LOCREF")
        if not locref.startswith("https"):
            locref = self.file_provider.apply_relative_path(
                self.descriptor_path, locref
            )

        return FileMetadata(
            id=id_,
            use=use,
            mdid=mdid,
            groupid=groupid,
            ref=FileReference(locref=str(locref), mdtype=mdtype, mimetype=mimetype),
        )

    def get_struct_maps(self) -> list[StructMap]:
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
                order_elem_type = order_elem.get_optional("TYPE")
                struct_map_items.append(
                    StructMapItem(
                        order=order_number,
                        label=label,
                        asset_id=asset_id,
                        type=order_elem_type,
                    )
                )

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
