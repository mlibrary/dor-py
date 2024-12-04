from dataclasses import dataclass
from typing import Any

@dataclass
class Event:
    pass

@dataclass
class PackageSubmitted(Event):
    package_identifier: str

@dataclass
class PackageReceived(Event):
    package_identifier: str
    tracking_identifier: str

@dataclass
class PackageVerified(Event):
    package_identifier: str
    tracking_identifier: str

# Need to move this to a different file ? - Move it to model.py and import TBD
@dataclass(frozen=True)
class Coordinator:
    username: str
    email: str

@dataclass(frozen=True)
class VersionInfo():
    coordinator: Coordinator
    message: str

@dataclass
class ItemUnpacked(Event):
    identifier: str
    resources: list[Any]
    tracking_identifier: str
    version_info: VersionInfo
    package_identifier: str

@dataclass
class ItemStored(Event):
    identifier: str
    tracking_identifier: str