# from dataclasses import dataclass, field
from dataclasses import field
# from pydantic.dataclasses import dataclass
from pydantic import BaseModel

import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path

class AlternateIdentifier(BaseModel):
    type: str
    id: str


class Agent(BaseModel):
    address: str
    role: str


class PreservationEvent(BaseModel):
    identifier: str
    type: str
    datetime: datetime
    detail: str
    agent: Agent


class FileReference(BaseModel):
    locref: str
    mdtype: str = None
    mimetype: str = None


class FileMetadata(BaseModel):
    id: str
    use: str
    mdid: str = None
    groupid: str = None
    ref: FileReference = None


class StructMapType(Enum):
    PHYSICAL = "PHYSICAL"
    LOGICAL = "LOGICAL"


class StructMapItem(BaseModel):
    order: int
    label: str
    asset_id: str
    type: str = None


class StructMap(BaseModel):
    id: str
    type: StructMapType
    items: list[StructMapItem]


class PackageResource(BaseModel):
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