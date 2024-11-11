from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class RecordStatus(Enum):
    STAGE = "stage"
    STORE = "store"

@dataclass
class Actor():
    address: str
    role: str

@dataclass
class PreservationEvent():
    identifier: str
    type: str
    datetime: datetime
    detail: str
    actor: Actor

class FileMetadataFileType(Enum):
    TECHNICAL = "TECHNICAL"

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
    events: list[PreservationEvent]
    files: list[AssetFile]

class StructMapType(Enum):
    PHYSICAL = "PHYSICAL"
    LOGICAL = "LOGICAL"

@dataclass
class StructMapItem():
    order: int
    label: str
    asset_id: str

@dataclass
class StructMap():
    id: str
    type: StructMapType
    items: list[StructMapItem]

@dataclass
class RepositoryItem():
    id: str
    record_status: RecordStatus
    events: list[PreservationEvent]
    struct_map: StructMap
    assets: list[Asset]
