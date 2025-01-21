from abc import ABC, abstractmethod
from pathlib import Path


class FileProvider(ABC):
    @abstractmethod
    def apply_relative_path(self, base_path: Path, path_to_apply: str) -> Path:
        pass

    @abstractmethod
    def get_descriptor_dir(self, file_path: Path) -> Path:
        pass

    @abstractmethod
    def get_norm_path(self, base_path: Path, path_to_apply: str) -> Path:
        pass

    @abstractmethod
    def get_combined_path(self, base_path: Path, path_to_apply: str) -> Path:
        pass

    @abstractmethod
    def clone_directory_structure(self, source_path: Path, destination_path: Path):
        pass

    @abstractmethod
    def get_environment_variable(self, env_key: str, default_value: str) -> str:
        pass

    @abstractmethod
    def delete_dir_and_contents(self, path: Path):
        pass

    @abstractmethod
    def create_directory(self, path: Path):
        pass

    @abstractmethod
    def create_directories(self, path: Path):
        pass