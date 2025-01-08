import os
from pathlib import Path


class Utils:
    
    @staticmethod
    def _apply_relative_path(descriptor_path: Path, path_to_apply: str) -> str:
        resolved_combined_path = path_to_apply
        if path_to_apply.startswith("../"):
            combined_path = os.path.join(descriptor_path, path_to_apply) 
            resolved_combined_path = str(os.path.normpath(combined_path))
        return resolved_combined_path