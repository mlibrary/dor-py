from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Set

from gateway.bundle import Bundle
from gateway.coordinator import Coordinator
from gateway.enumerations import LogOrder
from gateway.exceptions import ObjectDoesNotExistError, RepositoryGatewayError, StagedObjectAlreadyExistsError
from gateway.object_file import ObjectFile
from gateway.repository_gateway import RepositoryGateway
from gateway.version_info import VersionInfo


@dataclass(frozen=True)
class Version():
    number: int
    coordinator: Coordinator
    message: str
    date: datetime
    files: Set[Path]


@dataclass
class RepositoryObject:
    versions: list[Version]
    staged_files: Set[Path]


class FakeRepositoryGateway(RepositoryGateway):

    def __init__(self) -> None:
        self.store: dict[str, RepositoryObject] = dict()

    def create_repository(self):
        pass

    def has_object(self, object_id: str) -> bool:
        if object_id not in self.store:
            return False
        repo_object = self.store[object_id]
        return len(repo_object.versions) > 0

    def create_staged_object(self, id: str) -> None:
        if id in self.store:
            raise StagedObjectAlreadyExistsError()

        self.store[id] = RepositoryObject(staged_files=set(), versions=[])

    def stage_object_files(self, id: str, source_bundle: Bundle) -> None:
        file_paths = set(source_bundle.entries)
        if id not in self.store:
            raise ObjectDoesNotExistError()

        self.store[id].staged_files = self.store[id].staged_files.union(file_paths)

    def _get_latest_version(self, id: str) -> Version | None:
        if self.store[id].versions:
            return self.store[id].versions[-1]
        return None

    def commit_object_changes(
        self,
        id: str,
        coordinator: Coordinator,
        message: str,
        date: datetime = datetime.now(timezone.utc).astimezone(),
    ) -> None:
        if id not in self.store:
            raise ObjectDoesNotExistError()

        latest_version = self._get_latest_version(id)
        next_version_num = latest_version.number + 1 if latest_version else 1
        latest_files = latest_version.files if latest_version else set()
        files = latest_files.union(self.store[id].staged_files)

        self.store[id].versions.append(Version(
            number=next_version_num,
            coordinator=coordinator,
            message=message,
            date=date,
            files=files
        ))
        self.store[id].staged_files = set()

    def get_object_files(self, id: str, include_staged: bool = False) -> list[ObjectFile]:
        if id not in self.store:
            raise ObjectDoesNotExistError()

        latest_version = self._get_latest_version(id)
        file_paths = latest_version.files if latest_version else set()
        if include_staged:
            file_paths = file_paths.union(self.store[id].staged_files)

        object_files = []
        for file_path in file_paths:
            object_files.append(ObjectFile(logical_path=file_path, literal_path=file_path))
        return object_files

    def purge_object(self, id: str) -> None:
        if id in self.store:
            self.store.pop(id)

    def log(self, id: str, order: LogOrder = LogOrder.descending) -> list[VersionInfo]:
        version_log = []

        try:
            for v in self.store[id].versions:
                version_log.append(VersionInfo(version=v.number, author=v.coordinator,
                                               date=v.date, message=v.message))

            if order == LogOrder.descending:
                version_log = list(reversed(version_log))

            if len(version_log) == 0:
                raise RepositoryGatewayError

            return version_log
        except KeyError as e:
            raise RepositoryGatewayError() from e
