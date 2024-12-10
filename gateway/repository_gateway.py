from abc import ABCMeta, abstractmethod

from gateway.coordinator import Coordinator
from gateway.object_file import ObjectFile
from gateway.disk_package import DiskPackage

class RepositoryGateway(metaclass=ABCMeta):

    @abstractmethod
    def create_repository(self) -> None:
        pass

    @abstractmethod
    def create_staged_object(self, id: str) -> None:
        pass

    @abstractmethod
    def stage_object_files(self, id: str, source_package: DiskPackage) -> None:
        pass

    @abstractmethod
    def commit_object_changes(
        self,
        id: str,
        coordinator: Coordinator,
        message: str
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
