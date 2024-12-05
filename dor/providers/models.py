from dataclasses import dataclass, field
import uuid
from datetime import datetime


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
    mdtype: str
    mimetype: str = None


@dataclass
class FileMetadata:
    id: str
    use: str
    mdid: str = None
    ref: FileReference = None


@dataclass
class PackageResource:
    id: uuid.UUID
    type: str
    alternate_identifier: AlternateIdentifier
    events: list[PreservationEvent]
    file_metadata: list[FileMetadata]
    member_ids: list[str]
    # structure: list[Structure] || []
