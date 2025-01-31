import os
from pathlib import Path
import shutil
from dor.providers.file_provider import FileProvider


class FilesystemFileProvider(FileProvider):

    def apply_relative_path(self, base_path: Path, path_to_apply: str) -> Path:
        resolved_combined_path = self.get_norm_path(base_path, path_to_apply)
        final_path = resolved_combined_path.relative_to(base_path.parent)
        return final_path

    def get_descriptor_dir(self, file_path: Path) -> Path:
        return file_path.parent

    def get_norm_path(self, base_path: Path, path_to_apply: str) -> Path:
        combined_path = self.get_combined_path(base_path, path_to_apply)
        resolved_combined_path = Path(os.path.normpath(combined_path))
        return resolved_combined_path

    def get_combined_path(self, base_path: Path, path_to_apply: str) -> Path:
        return base_path / path_to_apply

    def clone_directory_structure(self, source_path: Path, destination_path: Path):
        shutil.copytree(source_path, destination_path)

    def delete_dir_and_contents(self, path: Path):
        shutil.rmtree(path, ignore_errors=True)

    def create_directory(self, path: Path):
        os.mkdir(path)

    def create_directories(self, path: Path):
        os.makedirs(path)
