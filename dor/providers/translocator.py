from dataclasses import dataclass
from pathlib import Path

from gateway.fake_repository_gateway import FakePackage


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
@dataclass
class Workspace:
    identifier: str
    root_identifier: str | None = None
    
    def package_directory(self) -> Path:
        return Path(self.identifier)
    
    def object_data_directory(self) -> Path:
        if self.root_identifier is None:
            raise Exception()
        return self.package_directory() / "data" / self.root_identifier
    
    def get_bundle(self, entries: list[Path]) -> FakePackage:
        return Bundle(
            root_path=self.object_data_directory(),
            entries=entries
        )


@dataclass
class Bundle:
    root_path: Path
    entries: list[Path]
    
    def get_file_paths(self) -> list[Path]:
        resolved_entries=[]
        for entry in self.entries:
            resolved_entries.append(self._apply_relative_path(self.root_path/"descriptor", entry))
        return resolved_entries    
          
    def _apply_relative_path(self, path: Path, path_to_apply: Path) -> Path:
        return (path / path_to_apply).resolve().relative_to(self.root_path)


class FakeTranslocator:

    def create_workspace_for_package(self, package_identifier: str) -> FakeWorkspace:
        return FakeWorkspace(package_identifier)