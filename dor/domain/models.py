import uuid
from enum import Enum
from datetime import datetime
from typing import Any

from pydantic import field_validator
from pydantic.dataclasses import dataclass

from gateway.coordinator import Coordinator
from dor.providers.models import PackageResource


@dataclass(frozen=True)
class VersionInfo():
    coordinator: Coordinator
    message: str


@dataclass
class Bin:
    identifier: uuid.UUID
    alternate_identifiers: list[str]
    common_metadata: dict[str, Any]
    package_resources: list[PackageResource]

    @field_validator("package_resources", mode='before')
    @classmethod
    def coerce_to_instance(cls, values):
        return [PackageResource(**v) if isinstance(v, dict) else v for v in values]


class WorkflowEventType(Enum):
    PACKAGE_SUBMITTED = "PackageSubmitted"
    PACKAGE_RECEIVED = "PackageReceived"
    PACKAGE_VERIFIED = "PackageVerified"
    PACKAGE_NOT_VERIFIED = "PackageNotVerified"
    PACKAGE_UNPACKED = "PackageUnpacked"
    PACKAGE_STORED = "PackageStored"
    BIN_CATALOGED = "BinCataloged"


@dataclass
class WorkflowEvent:
    identifier: uuid.UUID
    package_identifier: str
    tracking_identifier: str
    event_type: WorkflowEventType
    timestamp: datetime
    message: str | None
