from dataclasses import dataclass, field
import uuid6
from ulid import ULID

import hashlib
from enum import Enum

class FileUses(str, Enum):
    access = "ACCESS"
    source = "SOURCE"

@dataclass
class Md:
    use: str = None
    id: uuid6.UUID = field(default_factory=lambda: uuid6.uuid7())
    locref: str = None
    loctype: str = "URL"
    mdtype: str = None
    checksum: str = None


@dataclass
class MdGrp:
    use: str = None
    id: uuid6.UUID = field(default_factory=lambda: uuid6.uuid7())
    items: list[Md] = field(default_factory=list)


@dataclass
class File:
    use: str = None
    id: uuid6.UUID = field(default_factory=lambda: uuid6.uuid7())
    mdid: str = None
    group_id: str = None
    locref: str = None
    mimetype: str = None
    checksum: str = None


@dataclass
class FileGrp:
    use: str
    files: list[File] = field(default_factory=list)


def calculate_checksum(pathname):
    with pathname.open("rb") as f:
        digest = hashlib.file_digest(f, "sha512")
    return digest.hexdigest()

def generate_uuid():
    return str(uuid6.uuid7())

def generate_ulid():
    return str(ULID())

def generate_md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()