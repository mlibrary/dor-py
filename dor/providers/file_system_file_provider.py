import os
from pathlib import Path
from dor.providers.file_provider import FileProvider


class FilesystemHandler(FileProvider):

    def apply_relative_path(self, base_path: Path, path_to_apply: str) -> Path:
        combined_path = os.path.join(base_path, path_to_apply) 
        resolved_combined_path = Path(os.path.normpath(combined_path))
        return resolved_combined_path
    
    def get_data_dir(self, file_path: Path) -> Path:
        return file_path.parent