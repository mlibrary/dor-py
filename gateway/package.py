from abc import ABCMeta, abstractmethod
from pathlib import Path


class Package(metaclass=ABCMeta):

    @abstractmethod
    def get_root_path(self) -> Path:
        pass

    @abstractmethod
    def get_file_paths(self) -> list[Path]:
        pass
