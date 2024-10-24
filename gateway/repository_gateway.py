from abc import ABCMeta, abstractmethod

from gateway.coordinator import Coordinator
from gateway.package import Package

class RepositoryGateway(metaclass=ABCMeta):

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
    def read_object(self, id: str, output_path: str) -> None:
        pass

    @abstractmethod
    def purge_object(self, id: str) -> None:
        pass

    @abstractmethod
    def delete_object_file(
        self,
        id: str,
        file_path: str,
        coordinator: Coordinator,
        message: str
    ) -> None:
        pass

    @abstractmethod
    def has_object(self, id: str) -> bool:
        pass

    @abstractmethod
    def get_file_paths(self, id: str) -> list[str]:
        pass

    @abstractmethod
    def get_storage_relative_file_paths(self, id: str) -> list[str]:
        pass

    # def get_versions?
