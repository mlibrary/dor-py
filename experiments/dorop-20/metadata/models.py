from pathlib import Path
from dataclasses import dataclass
from enum import Enum

class RecordStatus(Enum):
    STAGE = "stage"
    STORE = "store"

class FileMetadataFileType(Enum):
    TECHNICAL = 'TECHNICAL'

@dataclass
class FileMetadataFile:
    id: str
    type: FileMetadataFileType
    path: Path

@dataclass
class AssetFile:
    id: str
    path: Path
    metadata_file: FileMetadataFile

@dataclass
class Asset:
    id: str
    files: list[AssetFile]

@dataclass
class RepositoryItem():
    id: str
    record_status: RecordStatus
    asset_order: list[str]
    assets: list[Asset]
