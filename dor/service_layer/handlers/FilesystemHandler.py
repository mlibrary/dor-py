import os
from pathlib import Path
from dor.providers.FileProvider import FileProvider


class FilesystemHandler(FileProvider):

    def apply_relative_path(self, base_path: Path, path_to_apply: str) -> str:
        resolved_combined_path = path_to_apply
        if path_to_apply.startswith("../"):
            combined_path = os.path.join(base_path, path_to_apply) 
            resolved_combined_path = str(os.path.normpath(combined_path))
        return resolved_combined_path
    
    def get_data_dir(self, file_path: Path) -> Path:
        return file_path.parent