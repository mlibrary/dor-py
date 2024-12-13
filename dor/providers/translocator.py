from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Callable

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
    
    def get_bundle(self, entries: list[Path]) -> Bundle:
        return Bundle(
            root_path=self.object_data_directory(),
            entries=entries
        )


class FakeTranslocator:

    def create_workspace_for_package(self, package_identifier: str) -> FakeWorkspace:
        return FakeWorkspace(package_identifier)


class Translocator():

    def __init__(self, inbox_path: Path, workspaces_path: Path, minter: Callable[[], str]) -> None:
        self.inbox_path = inbox_path
        self.workspaces_path = workspaces_path
        self.minter = minter

    def create_workspace_for_package(self, package_identifier: str) -> Workspace:
        workspace_id = self.minter()
        workspace_path = self.workspaces_path / workspace_id
        shutil.copytree(self.inbox_path / package_identifier, workspace_path)
        return Workspace(str(workspace_path))
