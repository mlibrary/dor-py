from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from dor.providers.file_provider import FileProvider
from gateway.bundle import Bundle


@dataclass
class FakeWorkspace:
    identifier: str
    root_identifier: str | None = None

    def package_directory(self) -> Path:
        return Path(self.identifier)

    def object_data_directory(self) -> Path:
        if self.root_identifier is None:
            raise Exception()
        return self.package_directory() / "data"

    def get_bundle(self, entries: list[Path]) -> Bundle:
        return Bundle(
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
        return self.package_directory() / "data"

    def get_bundle(self, entries: list[Path]) -> Bundle:
        return Bundle(
            root_path=self.object_data_directory(),
            entries=entries
        )


class FakeTranslocator:

    def create_workspace_for_package(self, package_identifier: str) -> FakeWorkspace:
        return FakeWorkspace(package_identifier)


class Translocator():

    def __init__(self, inbox_path: Path, workspaces_path: Path, minter: Callable[[], str], file_provider: FileProvider) -> None:
        self.inbox_path = inbox_path
        self.workspaces_path = workspaces_path
        self.minter = minter
        self.file_provider = file_provider

    def create_workspace_for_package(self, package_identifier: str) -> Workspace:
        workspace_id = self.minter()
        workspace_path = self.workspaces_path / workspace_id
        self.file_provider.clone_directory_structure(
            self.inbox_path / package_identifier, workspace_path
        )
        return Workspace(str(workspace_path))
