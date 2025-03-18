from abc import ABCMeta, abstractmethod
from datetime import datetime, timezone

from gateway.bundle import Bundle
from gateway.coordinator import Coordinator
from gateway.object_file import ObjectFile
from gateway.version_info import VersionInfo


class RepositoryGateway(metaclass=ABCMeta):

    @abstractmethod
    def create_repository(self) -> None:
        pass

    @abstractmethod
    def create_staged_object(self, id: str) -> None:
        pass

    @abstractmethod
    def stage_object_files(self, id: str, source_bundle: Bundle) -> None:
        pass

    @abstractmethod
    def commit_object_changes(
        self,
        id: str,
        coordinator: Coordinator,
        message: str,
        date: datetime = datetime.now(timezone.utc).astimezone()
    ) -> None:
        pass

    @abstractmethod
    def purge_object(self, id: str) -> None:
        pass

    @abstractmethod
    def has_object(self, id: str) -> bool:
        pass

    @abstractmethod
    def get_object_files(self, id: str, include_staged: bool = False) -> list[ObjectFile]:
        pass

    @abstractmethod
    def log(self, id: str, reversed: bool = True) -> list[VersionInfo]:
        pass
