from dataclasses import dataclass, field
import uuid6
from ulid import ULID

import hashlib
from enum import Enum

from pathlib import Path

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
            return (
                self.fakers["en_US"]
                .date_time_between(start_date=start_date)
                .strftime("%Y-%m-%dT00:00:00Z")
            )
        return (
            self.fakers["en_US"]
            .date_time_between_dates(
                datetime_start=datetime(1991, 1, 1, 0, 0, 0),
                datetime_end=datetime(2027, 12, 31, 23, 59, 59),
            )
            .strftime("%Y-%m-%dT%H:%M:%SZ")
        )

    def __getitem__(self, locale):
        return self.fakers[locale]

    def __getattr__(self, name):
        op = getattr(self.fakers["en_US"], name, None)
        if callable(op):
            return op
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )


class _Enum(Enum):
    def __str__(self):
        return self.value

class UseFunctions(str, _Enum):
    service = "function:service"
    source = "function:source"
    provenance = "function:provenance"
    preservation = "function:preservation"
    event = "function:event"
    technical = "function:technical"


class UseFormats(str, _Enum):
    image = "format:image"
    audiovidual = "format:audiovisual"
    audio = "format:audio"
    text_coordinates = "format:text-coordinate"
    text_plain = "format:text-plain"
    text_annotations = "format:text-annotation"
    text_encoded = "format:text-encoded"


class StructureTypes(str, _Enum):
    physical = "structure:physical"
    contents = "structure:contents"
    grid = "structure:grid"
    page = "structure:page"


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
    collid: str = "dlxs"
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


@dataclass
class FileInfo:
    identifier: str
    basename: str
    uses: list[UseFunctions | UseFormats]
    mimetype: str

    @property
    def place(self):
        return "data"

    @property
    def ext(self):
        match self.mimetype:
            case "image/jpeg":
                return "jpg"
            case "text/plain":
                return "txt"
            case "text/xml+premis":
                return "premis.xml"
            case "text/xml+mix":
                return "mix.xml"
            case "text/xml+textmd":
                return "textmd.xml"
            case "application/json+schema":
                return "json"
            case "application/json":
                return "json"
            case "_":
                return "bin"

    @property
    def filename(self):
        return f"{self.basename}.{flatten_use(*self.uses, delim='.')}.{self.ext}"

    @property
    def locref(self):
        return f"{self.identifier}/{self.place}/{self.filename}"

    def __str__(self):
        return self.filename

    def encode(self, encoding):
        return self.filename.encode(encoding)

    def metadata(self, use, mimetype):
        return MetadataFileInfo(
            identifier=self.identifier,
            basename=self.filename,
            uses=[use],
            mimetype=mimetype,
        )

    @property
    def path(self):
        return Path(self.place, self.filename)


@dataclass
class MetadataFileInfo(FileInfo):
    mdtype_: str = None

    @property
    def place(self):
        return "metadata"

    @property
    def mdtype(self):
        if self.mdtype_:
            return self.mdtype_
        match self.mimetype:
            case "text/xml+premis":
                return "PREMIS"
            case "text/xml+mix":
                return "NISOIMG"
            case "text/xml+textmd":
                return "TEXTMD"
            case "application/json":
                return "schema:generic"
            case "_":
                return "OTHER"


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
    return hashlib.md5(s.encode("utf-8")).hexdigest()


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


def flatten_use(*uses, delim=" "):
    # this is shameless pea green
    return delim.join([u.value for u in uses])
