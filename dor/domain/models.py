from dataclasses import dataclass
from typing import Self
from pathlib import Path

from gateway.coordinator import Coordinator
from gateway.fake_repository_gateway import FakePackage

@dataclass(frozen=True)
class VersionInfo():
    coordinator: Coordinator
    message: str


@dataclass
class FakeWorkspace:
    identifier: str
    root_identifier: str | None = None

    def package_directory(self) -> Path:
        return Path(self.identifier)
    
    def object_data_directory(self) -> Path:
        if self.root_identifier is None:
            raise Exception()
        return self.package_directory() / "data" / self.root_identifier

    def get_bundle(self, entries: list[Path]) -> FakePackage:
        return FakePackage(
            root_path=self.object_data_directory(),
            entries=entries
        )
