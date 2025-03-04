from dataclasses import dataclass, field
import uuid6
from ulid import ULID

import hashlib
from enum import Enum

from datetime import datetime

from faker.factory import Factory

from dor.settings import S


class Fakish:
    def __init__(self, seed=-1):
        locales = ["it_IT", "en_US", "ja_JP"]
        self.fakers = {}
        for locale in locales:
            _Faker = Factory.create
            self.fakers[locale] = _Faker(locale=locale)
            self.fakers[locale].seed(seed if seed > -1 else None)

    def get_datetime(self, start_date=None):
        if start_date:
            return self.fakers["en_US"].date_time_between(start_date=start_date)\
                .strftime("%Y-%m-%dT00:00:00Z")
        return self.fakers["en_US"].date_time_between_dates(
            datetime_start=datetime(1991, 1, 1, 0, 0, 0),
            datetime_end=datetime(2027, 12, 31, 23, 59, 59),
        ).strftime("%Y-%m-%dT%H:%M:%SZ")

    def __getitem__(self, locale):
        return self.fakers[locale]

    def __getattr__(self, name):
        op = getattr(self.fakers["en_US"], name, None)
        if callable(op):
            return op
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

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
    mimetype: str = None


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
        if self.uuid:
            self.start = self.uuid.int
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


class IdGenerator:
    def __init__(self, identifier):
        self.identifier = identifier
        self.counter = 0

    def __call__(self):
        self.counter += 1
        return generate_uuid(base=16 * 16 * self.identifier.start + self.counter)


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

def make_paths(pathname):
    pathname.mkdir()
    for d in ["data", "descriptor", "metadata"]:
        d_pathname = pathname.joinpath(d)
        d_pathname.mkdir()
    return pathname

_fakers = {}

def reset_fakers():
    global _fakers
    _fakers.clear()

def get_faker(role="default"):
    global _fakers
    if not role in _fakers:
        _fakers[role] = Fakish(S.seed)
    return _fakers[role]


def get_datetime():
    fake = get_faker()
    return fake.date_time_between_dates(
        datetime_start=datetime(1991, 1, 1, 0, 0, 0),
        datetime_end=datetime(2027, 12, 31, 23, 59, 59),
    ).strftime("%Y-%m-%dT%H:%M:%SZ")
