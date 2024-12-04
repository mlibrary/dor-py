from dataclasses import dataclass
from pathlib import Path
from typing import Set
from dor.domain.models import Coordinator


class FakePackage:
    package_identifier: str
    entries: list[Path]

    def get_paths(self) -> list[Path]:
        return self.entries

@dataclass
class RepositoryObject:
    staged_files: Set[str]
    files: Set[str]

# subclass Repository Gateway some day?
class FakeRepositoryGateway():

    def __init__(self) -> None:
        self.store: dict[str, RepositoryObject] = dict()

    def create_repository(self):
        pass

    def has_object(self, object_id: str):
        return object_id in self.store and len(self.store[object_id].files) > 0

    def create_staged_object(self, id: str) -> None:
        self.store[id] = RepositoryObject(staged_files=set(), files=set())

    def stage_object_files(self, id: str, source_package: FakePackage) -> None:
        file_paths = set(source_package.get_paths())
        if id not in self.store:
            raise Exception()
        self.store[id].staged_files = self.store[id].staged_files.union(file_paths)

    def commit_object_changes(
        self,
        id: str,
        coordinator: Coordinator,
        message: str
    ) -> None:
        if id not in self.store:
            raise Exception()
        self.store[id].files = self.store[id].files.union(self.store[id].staged_files)
        self.store[id].staged_files = set()