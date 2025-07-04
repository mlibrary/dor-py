from dataclasses import dataclass
from typing import Any

from dor.domain.models import VersionInfo
from dor.providers.models import PackageResource


@dataclass
class Event:
    pass

# integration event
@dataclass
class FileSetCreated(Event):
    type = 'fileset.created'
    identifier: str
    job_idx: int


# integration event; moves to packaging
@dataclass
class PackageGenerated(Event):
    type = 'package.generated'
    package_identifier: str

# integration event; moves to ingest
# some naming considerations:
#   - package ingested
#   - submission processed
#   - ingest successful
#   - resource created
#   - resource updated
class PackageIngested(Event):
    type = 'package.ingested'
    package_identifier: str
    tracking_identifier: str


@dataclass(kw_only=True)
class PackageEvent(Event):
    package_identifier: str
    tracking_identifier: str
    update_flag: bool = False


# internal/domain event; moves to ingest
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
    workspace_identifier: str
    revision_number: int


@dataclass
class RevisionCataloged(PackageEvent):
    identifier: str
    workspace_identifier: str
