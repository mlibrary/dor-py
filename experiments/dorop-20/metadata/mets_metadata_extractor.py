from pathlib import Path

from metadata.exceptions import MetadataFileNotFoundError
from metadata.models import (
    Asset,
    AssetFile,
    FileMetadataFile,
    FileMetadataFileType,
    RecordStatus,
    RepositoryItem
)

from lxml import etree

class MetsMetadataExtractor():
    root_metadata_file_suffix = "root.mets2.xml"
    asset_prefix = "urn:umich.edu:dor:asset:"
   
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

    @staticmethod
    def get_metadata_tree(file_path: Path):
        tree = etree.fromstring(text=file_path.read_text())
        return tree
    
    @classmethod
    def get_asset(cls, file_path: Path):
        tree = cls.get_metadata_tree(file_path)
        asset_id = tree.get("OBJID").replace(cls.asset_prefix, "")

        asset_file_elems = tree.findall(".//METS:file", cls.namespaces)
        asset_files = []
        for asset_file_elem in asset_file_elems:
            asset_file_id = asset_file_elem.get("ID")
            flocat_elem = asset_file_elem.find("METS:FLocat", cls.namespaces)
            asset_path = Path(flocat_elem.get("LOCREF").replace("../", ""))
            
            file_metadata_file_id = asset_file_elem.get("MDID")
            file_metadata_file_elem = tree.find(f".//METS:md[@ID='{file_metadata_file_id}']", cls.namespaces)
            file_metadata_file_id = file_metadata_file_elem.get("ID")
            file_metadata_file_type = file_metadata_file_elem.get("USE")
            file_metadata_file_loc_elem = file_metadata_file_elem.find("METS:mdRef", cls.namespaces)
            file_metadata_file_path = file_metadata_file_loc_elem.get("LOCREF").replace("../", "")

            asset_files.append(AssetFile(
                id=asset_file_id,
                path=Path(asset_path),
                metadata_file=FileMetadataFile(
                    id=file_metadata_file_id,
                    type=FileMetadataFileType[file_metadata_file_type],
                    path=Path(file_metadata_file_path)
                )
            ))

        return Asset(id=asset_id, files=asset_files)

    def find_root_metadata_file_path(self) -> Path | None:
        for file_path in self.get_file_paths(self.content_path):
            if str(file_path).endswith(self.root_metadata_file_suffix):
                return file_path

    def __init__(self, content_path: Path):
        self.content_path: Path = content_path

        file_path = self.find_root_metadata_file_path()
        if not file_path:
            raise MetadataFileNotFoundError
        self.root_tree = self.get_metadata_tree(file_path)

    def get_identifier(self) -> str:
        return self.root_tree.get("OBJID")

    def get_record_status(self) -> str:
        mets_header = self.root_tree.find("METS:metsHdr", self.namespaces)
        return mets_header.get('RECORDSTATUS')

    def get_asset_file_paths(self) -> list[Path]:
        struct_map = self.root_tree.find(".//METS:structMap", self.namespaces)
        order_elems = struct_map.findall(".//METS:div[@ORDER]", self.namespaces)
        
        asset_file_paths: list[Path] = []
        for order_elem in order_elems:
            mptr = order_elem.find("METS:mptr", self.namespaces)
            asset_file_name: str = mptr.get("LOCREF")
            asset_file_paths.append(Path("descriptor") / asset_file_name)
        return asset_file_paths

    def get_asset_order(self) -> list[str]:
        struct_map = self.root_tree.find(".//METS:structMap", self.namespaces)
        order_elems = struct_map.findall(".//METS:div[@ORDER]", self.namespaces)
        
        asset_dict = dict()
        for order_elem in order_elems:
            order_number = int(order_elem.get("ORDER"))
            mptr = order_elem.find("METS:mptr", self.namespaces)
            asset_file_name: str = mptr.get("LOCREF")
            # better way to get the ID?
            asset_id = asset_file_name.replace(".mets2.xml", "")
            asset_dict[order_number] = asset_id
        sorted_keys = sorted(asset_dict.keys())
        return [asset_dict[key] for key in sorted_keys]
    
    def get_repository_item(self) -> RepositoryItem:
        return RepositoryItem(
            id=self.get_identifier(),
            record_status=RecordStatus[self.get_record_status().upper()],
            asset_order=self.get_asset_order(),
            assets=[
                self.get_asset(self.content_path / asset_file_path)
                for asset_file_path in self.get_asset_file_paths()
            ]
        )
