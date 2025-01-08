import uuid
from dataclasses import dataclass
from typing import Any

from gateway.coordinator import Coordinator


@dataclass(frozen=True)
class VersionInfo():
    coordinator: Coordinator
    message: str

@dataclass
class Bin:
    identifier: uuid.UUID
    alternate_identifiers: list[str]
    common_metadata: dict[str, Any]
