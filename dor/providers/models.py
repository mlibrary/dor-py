from dataclasses import dataclass, field
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path

@dataclass
class AlternateIdentifier:
    type: str
    id: str


@dataclass
class Agent:
    address: str
    role: str


@dataclass
class PreservationEvent:
    identifier: str
    type: str
    datetime: datetime
    detail: str
    agent: Agent


@dataclass
class FileReference:
    locref: str
    mdtype: str = None
    mimetype: str = None


@dataclass
class FileMetadata:
    id: str
    use: str
    mdid: str = None
    groupid: str = None
    ref: FileReference = None


class StructMapType(Enum):
    PHYSICAL = "PHYSICAL"
    LOGICAL = "LOGICAL"


@dataclass
class StructMapItem:
    order: int
    label: str
    asset_id: str
    type: str = None


@dataclass
class StructMap:
    id: str
    type: StructMapType
    items: list[StructMapItem]


@dataclass
class PackageResource:
    id: uuid.UUID
    type: str
    alternate_identifier: AlternateIdentifier
    events: list[PreservationEvent]
    metadata_files: list[FileMetadata] = field(default_factory=list)
    data_files: list[FileMetadata] = field(default_factory=list)
    struct_maps: list[StructMap] = field(default_factory=list)

    def get_entries(self) -> list[Path]:
        entries = []
        for file_metadata in self.metadata_files:
            if not file_metadata.ref.locref.startswith("https://"):
                entries.append(Path(file_metadata.ref.locref))

        for file_metadata in self.data_files:
            entries.append(Path(file_metadata.ref.locref))

        return entries