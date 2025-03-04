from dataclasses import field
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel
from pydantic.dataclasses import dataclass


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
    mdtype: str | None = None
    mimetype: str | None = None


@dataclass
class FileMetadata:
    id: str
    use: str
    ref: FileReference
    mdid: str | None = None
    groupid: str | None = None


class StructMapType(Enum):
    PHYSICAL = "PHYSICAL"
    LOGICAL = "LOGICAL"


@dataclass
class StructMapItem:
    order: int
    label: str
    file_set_id: str
    type: str | None = None


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
    root: bool = False

    def get_entries(self) -> list[Path]:
        entries: list[Path] = []
        for file_metadata in self.metadata_files:
            if not file_metadata.ref.locref.startswith("https://"):
                entries.append(Path(file_metadata.ref.locref))

        for file_metadata in self.data_files:
            entries.append(Path(file_metadata.ref.locref))

        return entries


# Packager

class DepositGroup(BaseModel):
    identifier: str
    date: datetime


class PackagerConfig(BaseModel):
    deposit_group: DepositGroup


class PackageFileMetadata(BaseModel):
    use: str
    mimetype: str
    mdtype: Optional[str] = None
    data: Any


class PackageStructureItem(BaseModel):
    order: str
    orderlabel: str
    type: str
    locref: str


class PackageStructure(BaseModel):
    type: str
    items: list[PackageStructureItem]


class PackageMetadata(BaseModel):
    identifier: str
    md: list[PackageFileMetadata]
    structure: list[PackageStructure]

