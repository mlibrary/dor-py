from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from pydantic import BaseModel

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

class CommonMetadata(BaseModel):
    title: str
    author: str
    publication_date: datetime
    subjects: list[str]

class AssetFileUse(Enum):
    ACCESS = "ACCESS"
    SOURCE = "SOURCE"

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
    use: AssetFileUse
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
    rights: str | None
    events: list[PreservationEvent]
    common_metadata: CommonMetadata
    struct_map: StructMap
    assets: list[Asset]