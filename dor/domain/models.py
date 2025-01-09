import uuid
from dataclasses import dataclass
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
