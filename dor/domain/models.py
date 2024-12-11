from dataclasses import dataclass
from typing import Self
from pathlib import Path

from gateway.coordinator import Coordinator

@dataclass(frozen=True)
class VersionInfo():
    coordinator: Coordinator
    message: str


@dataclass
class Workspace:

    identifier: str

    @classmethod
    def find(cls, identifier) -> Self:
        return cls(identifier)

    def package_directory(self) -> Path:
        return Path("/tmp/package/directory")
    
    def object_data_directory(self, identifier: str) -> Path:
        return Path(self.package_directory()) / "data" / identifier
    