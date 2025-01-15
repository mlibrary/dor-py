from abc import ABC, abstractmethod
from pathlib import Path

class FileProvider(ABC):
    @abstractmethod
    def apply_relative_path(self, base_path: Path, path_to_apply: str) -> Path:
        pass

    @abstractmethod
    def get_data_dir(self, file_path: Path) -> Path:
        pass
    