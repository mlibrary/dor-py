from datetime import datetime
from pathlib import Path

from metadata.element_adapter import ElementAdapter
from metadata.exceptions import DataNotFoundError, MetadataFileNotFoundError
from metadata.models import (
    Actor, Asset, AssetFile, AssetFileUse, CommonMetadata, FileMetadataFile, FileMetadataFileType,
    PreservationEvent, RecordStatus, RepositoryItem, StructMap, StructMapItem, StructMapType
)

from pydantic import ValidationError

def apply_relative_path(path: Path, path_to_apply: Path) -> Path:
    return (path / path_to_apply).resolve(strict=True).relative_to(Path.cwd())

class PremisEventParser():
    def __init__(self, elem: ElementAdapter):
        self.elem: ElementAdapter = elem

    def get_event(self) -> PreservationEvent:
        event_identifier = self.elem.find(".//PREMIS:eventIdentifierValue").text
        event_type = self.elem.find(".//PREMIS:eventType").text
        event_datetime = self.elem.find(".//PREMIS:eventDateTime").text
        event_detail = self.elem.find(".//PREMIS:eventDetail").text
        actor_role = self.elem.find(".//PREMIS:linkingAgentIdentifierType").text
        actor_address = self.elem.find(".//PREMIS:linkingAgentIdentifierValue").text
        return PreservationEvent(
            identifier=event_identifier,
            type=event_type,
            datetime=datetime.fromisoformat(event_datetime),
            detail=event_detail,
            actor=Actor(address=actor_address, role=actor_role)
        )

class CommonMetadataParser():

    def __init__(self, metadata_path: Path):
        self.metadata_path: Path = metadata_path
        try:
            self.text = self.metadata_path.read_text()
        except FileNotFoundError as e:
            raise MetadataFileNotFoundError from e

    def get_metadata(self) -> CommonMetadata:
        try:
            return CommonMetadata.model_validate_json(self.text)
        except ValidationError as e:
            raise DataNotFoundError("Common metadata parsing failed") from e

class MetsAssetParser():
    asset_prefix = "urn:umich.edu:dor:asset:"

    namespaces: dict[str, str] = {
        "METS": "http://www.loc.gov/METS/v2",
        "PREMIS": "http://www.loc.gov/premis/v3"
    }

    def __init__(self, file_path: Path):
        self.file_path = file_path
        try:
            text = self.file_path.read_text()
        except FileNotFoundError as e:
            raise MetadataFileNotFoundError from e
        self.tree: ElementAdapter = ElementAdapter.from_string(text, self.namespaces)

    def get_events(self) -> list[PreservationEvent]:
        event_elems = self.tree.findall(".//PREMIS:event")
        return [PremisEventParser(event_elem).get_event() for event_elem in event_elems]

    def get_asset(self) -> Asset:
        asset_id = self.tree.get("OBJID").replace(self.asset_prefix, "")

        asset_file_elems = self.tree.findall(".//METS:file")
        asset_files = []
        for asset_file_elem in asset_file_elems:
            asset_file_id = asset_file_elem.get("ID")
            asset_file_use = asset_file_elem.get("USE")
            flocat_elem = asset_file_elem.find("METS:FLocat")
            asset_path = apply_relative_path(self.file_path.parent, Path(flocat_elem.get("LOCREF")))
            file_metadata_file_id = asset_file_elem.get("MDID")
            file_metadata_file_elem = self.tree.find(
                f".//METS:md[@ID='{file_metadata_file_id}']"
            )
            file_metadata_file_id = file_metadata_file_elem.get("ID")
            file_metadata_file_type = file_metadata_file_elem.get("USE")
            file_metadata_file_loc_elem = file_metadata_file_elem.find("METS:mdRef")
            file_metadata_file_path = apply_relative_path(
                self.file_path.parent, Path(file_metadata_file_loc_elem.get("LOCREF"))
            )

            asset_files.append(AssetFile(
                id=asset_file_id,
                path=Path(asset_path),
                use=AssetFileUse[asset_file_use],
                metadata_file=FileMetadataFile(
                    id=file_metadata_file_id,
                    type=FileMetadataFileType[file_metadata_file_type],
                    path=Path(file_metadata_file_path)
                )
            ))

        return Asset(id=asset_id, events=self.get_events(), files=asset_files)

class MetsMetadataParser():
    root_metadata_file_suffix = "root.mets2.xml"
   
    namespaces: dict[str, str] = {
        "METS": "http://www.loc.gov/METS/v2",
        "PREMIS": "http://www.loc.gov/premis/v3"
    }

    @staticmethod
    def get_file_paths(root_path: Path) -> list[Path]:
        paths = []
        for dirpath, _, filenames in root_path.walk():
            for filename in filenames:
                full_path = dirpath / filename
                paths.append(full_path)
        return paths

    def find_root_metadata_file_path(self) -> Path | None:
        for file_path in self.get_file_paths(self.content_path):
            if str(file_path).endswith(self.root_metadata_file_suffix):
                return file_path
        return None

    def __init__(self, content_path: Path):
        self.content_path: Path = content_path

        file_path = self.find_root_metadata_file_path()
        if not file_path:
            raise MetadataFileNotFoundError
        self.file_path: Path = file_path
        self.root_tree = ElementAdapter.from_string(self.file_path.read_text(), self.namespaces)

    def get_identifier(self) -> str:
        return self.root_tree.get("OBJID")

    def get_record_status(self) -> RecordStatus:
        mets_header = self.root_tree.find("METS:metsHdr")
        status = mets_header.get('RECORDSTATUS')
        return RecordStatus[status.upper()]

    def get_rights_info(self) -> str | None:
        md_rights_elem = self.root_tree.find(".//METS:md[@USE='RIGHTS']")
        child = md_rights_elem.get_children()[0]
        if child.tag == "METS:mdRef":
            return child.get("LOCREF")
        else:
            return None

    def get_asset_file_paths(self) -> list[Path]:
        struct_map = self.root_tree.find(".//METS:structMap")
        order_elems = struct_map.findall(".//METS:div[@ORDER]")
        
        asset_file_paths: list[Path] = []
        for order_elem in order_elems:
            mptr = order_elem.find("METS:mptr")
            asset_file_name: str = mptr.get("LOCREF")
            asset_file_paths.append(Path("descriptor") / asset_file_name)
        return asset_file_paths

    def get_events(self) -> list[PreservationEvent]:
        event_elems = self.root_tree.findall(".//PREMIS:event")
        return [PremisEventParser(event_elem).get_event() for event_elem in event_elems]

    def get_common_metadata(self) -> CommonMetadata:
        md_elem = self.root_tree.find(".//METS:md[@USE='DESCRIPTIVE/COMMON']")
        mdref_elem = md_elem.find("METS:mdRef")
        metadata_rel_path = mdref_elem.get("LOCREF")
        metadata_file_path = apply_relative_path(self.file_path.parent, Path(metadata_rel_path))
        return CommonMetadataParser(metadata_file_path).get_metadata()

    def get_repository_item(self) -> RepositoryItem:
        struct_map_elem = self.root_tree.find(".//METS:structMap")
        struct_map_id = struct_map_elem.get("ID")
        struct_map_type = struct_map_elem.get("TYPE")
        
        order_elems = struct_map_elem.findall(".//METS:div[@ORDER]")

        assets = []
        struct_map_items = []
        for order_elem in order_elems:
            order_number = int(order_elem.get("ORDER"))
            label = order_elem.get("LABEL")
            mptr_elem = order_elem.find("METS:mptr")
            asset_file_name: str = mptr_elem.get("LOCREF")
            asset_file_path = apply_relative_path(self.file_path.parent, Path(asset_file_name))
            asset = MetsAssetParser(asset_file_path).get_asset()
            assets.append(asset)
            struct_map_items.append(StructMapItem(
                order=order_number,
                label=label,
                asset_id=asset.id
            ))

        return RepositoryItem(
            id=self.get_identifier(),
            record_status=self.get_record_status(),
            events=self.get_events(),
            rights=self.get_rights_info(),
            common_metadata=self.get_common_metadata(),
            struct_map=StructMap(
                id=struct_map_id,
                type=StructMapType[struct_map_type.upper()],
                items=struct_map_items
            ),
            assets=assets
        )
