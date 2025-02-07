import uuid
from enum import Enum
from datetime import datetime, UTC
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
class Revision:
    identifier: uuid.UUID
    alternate_identifiers: list[str]
    revision_number: int
    created_at: datetime
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
    REVISION_CATALOGED = "RevisionCataloged"


@dataclass
class WorkflowEvent:
    identifier: uuid.UUID
    package_identifier: str
    tracking_identifier: str
    event_type: WorkflowEventType
    timestamp: datetime
    message: str | None

    @classmethod
    def create(
        cls,
        package_identifier: str,
        tracking_identifier: str,
        event_type: WorkflowEventType,
        message: str | None
    ):
        return cls(
            identifier=uuid.uuid4(),
            package_identifier=package_identifier,
            tracking_identifier=tracking_identifier,
            event_type=event_type,
            timestamp=datetime.now(tz=UTC),
            message=message
        )
