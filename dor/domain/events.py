from dataclasses import dataclass
from typing import Any

from dor.domain.models import VersionInfo
from dor.providers.models import PackageResource


@dataclass
class Event:
    pass


@dataclass
class PackageEvent(Event):
    package_identifier: str
    tracking_identifier: str


@dataclass
class PackageSubmitted(PackageEvent):
    pass

@dataclass
class PackageReceived(PackageEvent):
    workspace_identifier: str


@dataclass
class PackageVerified(PackageEvent):
    workspace_identifier: str


@dataclass
class PackageNotVerified(PackageEvent):
    message: str


@dataclass
class PackageUnpacked(PackageEvent):
    identifier: str
    resources: list[PackageResource]
    version_info: VersionInfo
    workspace_identifier: str


@dataclass
class PackageStored(PackageEvent):
    identifier: str
    resources: list[PackageResource]

@dataclass
class VersionCataloged(PackageEvent):
    identifier: str
