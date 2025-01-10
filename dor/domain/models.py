import uuid
# from dataclasses import dataclass, field
from dataclasses import field
from pydantic import field_validator
from pydantic.dataclasses import dataclass

from typing import Any

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