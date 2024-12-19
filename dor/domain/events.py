from dataclasses import dataclass
from typing import Any

from dor.domain.models import VersionInfo


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
    workspace_identifier: str


@dataclass
class PackageVerified(Event):
    package_identifier: str
    tracking_identifier: str
    workspace_identifier: str


@dataclass
class PackageNotVerified(Event):
    package_identifier: str
    tracking_identifier: str
    message: str


@dataclass
class PackageUnpacked(Event):
    identifier: str
    resources: list[Any]
    tracking_identifier: str
    version_info: VersionInfo
    workspace_identifier: str
    package_identifier: str


@dataclass
class PackageStored(Event):
    identifier: str
    tracking_identifier: str
