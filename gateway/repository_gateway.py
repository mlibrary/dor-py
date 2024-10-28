from abc import ABCMeta, abstractmethod

from gateway.coordinator import Coordinator
from gateway.file_mapping import FileMapping
from gateway.package import Package

class RepositoryGateway(metaclass=ABCMeta):

    @abstractmethod
    def create_empty_object(self, id: str) -> None:
        pass

    @abstractmethod
    def stage_object_files(
        self,
        id: str,
        source_package: Package
    ) -> None:
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
    def get_file_paths(self, id: str) -> list[str]:
        pass

    @abstractmethod
    def get_file_mappings(self, id: str) -> list[FileMapping]:
        pass
