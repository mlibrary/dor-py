from datetime import datetime
import uuid
from pathlib import Path

from utils.element_adapter import ElementAdapter
from .models import (
    Agent,
    AlternateIdentifier,
    FileMetadata,
    FileReference,
    PreservationEvent,
    StructMap,
    StructMapItem,
    StructMapType,
)


class PreservationEventFileParser:
    namespaces: dict[str, str] = {
        "PREMIS": "http://www.loc.gov/premis/v3",
    }

    def __init__(self, path: Path) -> None:
        self.path = path

    def get_event(self) -> PreservationEvent:
        premis_tree = ElementAdapter.from_string(self.path.read_text(), self.namespaces)
        event_elem = premis_tree.find(".//PREMIS:event")
        event_identifier = event_elem.find(".//PREMIS:eventIdentifierValue").text
        event_type = event_elem.find(".//PREMIS:eventType").text
        event_datetime = event_elem.find(".//PREMIS:eventDateTime").text
        event_detail_elem = event_elem.find_optional(".//PREMIS:eventDetail")
        event_detail = event_detail_elem.text if event_detail_elem else event_detail_elem
        agent_role = event_elem.find(".//PREMIS:linkingAgentIdentifierType").text
        agent_address = event_elem.find(".//PREMIS:linkingAgentIdentifierValue").text
        return PreservationEvent(
            identifier=event_identifier,
            type=event_type,
            datetime=datetime.fromisoformat(event_datetime),
            detail=event_detail,
            agent=Agent(address=agent_address, role=agent_role),
        )


class DescriptorFileParser:
    namespaces: dict[str, str] = {
        "METS": "http://www.loc.gov/METS/v2",
    }

    def __init__(self, descriptor_file_path: Path):
        text = descriptor_file_path.read_text()
        self.tree: ElementAdapter = ElementAdapter.from_string(text, self.namespaces)

    def get_id(self):
        return uuid.UUID(self.tree.get("OBJID"))

    def get_type(self):
        hdr = self.tree.find("METS:metsHdr")
        return hdr.get("TYPE")

    def get_root(self):
        header = self.tree.find("METS:metsHdr")
        record_status = header.get_optional("RECORDSTATUS")
        return record_status == "root"

    def get_alternate_identifiers(self) -> list[AlternateIdentifier]:
        return [
            AlternateIdentifier(type=elem.get('TYPE'), id=elem.text)
            for elem in self.tree.findall("METS:metsHdr/METS:altRecordID")
        ]

    def get_preservation_event_paths(self) -> list[str]:
        locrefs = []
        for elem in self.tree.findall(".//METS:md[@USE='function:event']/METS:mdRef"):
            locrefs.append(elem.get('LOCREF'))
        return locrefs

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
        mdtype = md_ref_element.get_optional("MDTYPE")
        mimetype = md_ref_element.get_optional("MIMETYPE")

        return FileMetadata(
            id=id_,
            use=use,
            ref=FileReference(locref=locref, mdtype=mdtype, mimetype=mimetype),
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

        return FileMetadata(
            id=id_,
            use=use,
            mdid=mdid,
            groupid=groupid,
            ref=FileReference(locref=locref, mdtype=mdtype, mimetype=mimetype),
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
                mptr = order_elem.find("METS:mptr")
                locref_path = Path(mptr.get("LOCREF"))
                file_set_id = locref_path.parts[0]
                order_elem_type = order_elem.get_optional("TYPE")
                struct_map_items.append(
                    StructMapItem(
                        order=order_number,
                        label=label,
                        file_set_id=file_set_id,
                        type=order_elem_type,
                    )
                )

            struct_maps.append(
                StructMap(
                    id=struct_map_id,
                    type=StructMapType(struct_map_type),
                    items=struct_map_items,
                )
            )

        return struct_maps
