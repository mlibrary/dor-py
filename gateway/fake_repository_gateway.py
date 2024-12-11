from dataclasses import dataclass
from pathlib import Path
from typing import Set

from gateway.coordinator import Coordinator
from gateway.exceptions import ObjectDoesNotExistError, StagedObjectAlreadyExistsError
from gateway.object_file import ObjectFile
from gateway.package import Package
from gateway.repository_gateway import RepositoryGateway


class FakePackage(Package):

    def __init__(self, root_path: Path, entries: list[Path]) -> None:
        self.root_path: Path = root_path
        self.entries: list[Path] = entries

    def get_root_path(self) -> Path:
        return self.root_path

    def get_file_paths(self) -> list[Path]:
        return self.entries


@dataclass
class Version():
    number: int
    coordinator: Coordinator
    message: str


@dataclass
class RepositoryObject:
    versions: list[Version]
    staged_files: Set[Path]
    files: Set[Path]


class FakeRepositoryGateway(RepositoryGateway):

    def __init__(self) -> None:
        self.store: dict[str, RepositoryObject] = dict()

    def create_repository(self):
        pass

    def has_object(self, object_id: str):
        if object_id not in self.store:
            return False
        repo_object = self.store[object_id]
        return repo_object.versions

    def create_staged_object(self, id: str) -> None:
        if id in self.store:
            raise StagedObjectAlreadyExistsError()

        self.store[id] = RepositoryObject(staged_files=set(), files=set(), versions=[])

    def stage_object_files(self, id: str, source_package: Package) -> None:
        file_paths = set(source_package.get_file_paths())
        if id not in self.store:
            raise ObjectDoesNotExistError()

        self.store[id].staged_files = self.store[id].staged_files.union(file_paths)

    def commit_object_changes(
        self,
        id: str,
        coordinator: Coordinator,
        message: str
    ) -> None:
        if id not in self.store:
            raise ObjectDoesNotExistError()

        self.store[id].files = self.store[id].files.union(self.store[id].staged_files)
        self.store[id].staged_files = set()

        if not self.store[id].versions:
            next_version_num = 1
        else:
            next_version_num = self.store[id].versions[-1].number + 1

        self.store[id].versions.append(Version(
            number=next_version_num,
            coordinator=coordinator,
            message=message
        ))

    def get_object_files(self, id: str, include_staged: bool = False) -> list[ObjectFile]:
        if id not in self.store:
            raise ObjectDoesNotExistError()
        
        file_paths = self.store[id].files
        if include_staged:
            file_paths = file_paths.union(self.store[id].staged_files)

        object_files = []
        for file_path in file_paths:
            object_files.append(ObjectFile(logical_path=file_path, literal_path=file_path))
        return object_files

    def purge_object(self, id: str) -> None:
        if id not in self.store:
            raise ObjectDoesNotExistError()

        self.store.pop(id)
