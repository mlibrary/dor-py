import uuid
from dataclasses import field, dataclass
from datetime import datetime, UTC
from enum import Enum
from pathlib import Path
from typing import Self


class _Enum(Enum):
    def __str__(self):
        return self.value


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
    detail: str | None
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


class StructMapType(_Enum):
    physical = "structure:physical"
    contents = "structure:contents"
    manifest = "structure:manifest"
    grid = "structure:grid"
    page = "structure:page"


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
    alternate_identifiers: list[AlternateIdentifier] = field(default_factory=list)
    events: list[PreservationEvent] = field(default_factory=list)
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

    def has_alternate_identifier(self, identifier: AlternateIdentifier) -> bool:
        for alt_identifier in self.alternate_identifiers:
            if alt_identifier == identifier:
                return True
        return False


@dataclass
class DepositGroup:
    identifier: str
    date: datetime

    @classmethod
    def generate(cls) -> Self:
        return cls(
            identifier=str(uuid.uuid4()),
            date=datetime.now(tz=UTC)
        )
