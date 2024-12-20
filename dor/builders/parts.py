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
    group_id: uuid6.UUID = None
    mdid: str = None
    group_id: str = None
    locref: str = None
    mimetype: str = None
    checksum: str = None


@dataclass
class FileGrp:
    use: str
    files: list[File] = field(default_factory=list)

# utility class so asset identifiers can
# build on the start value
@dataclass
class Identifier:
    collid: str = 'dlxs'
    start: int = -1
    uuid: uuid6.UUID = None

    def __post_init__(self):
        if self.start >= 0:
            self.uuid = uuid6.UUID(int=self.start)
        else:
            self.uuid = uuid6.uuid7()
            self.start = self.uuid.int

    def __str__(self):
        return str(self.uuid)
    
    def __add__(self, other):
        return str(self) + other
    
    @property
    def alternate_identifier(self):
        return f"{self.collid}:{self.uuid.int:08d}"


def calculate_checksum(pathname):
    with pathname.open("rb") as f:
        digest = hashlib.file_digest(f, "sha512")
    return digest.hexdigest()

def generate_uuid(base=None):
    if base:
        return str(uuid6.UUID(int=base))
    return str(uuid6.uuid7())

def generate_ulid():
    return str(ULID())

def generate_md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()
