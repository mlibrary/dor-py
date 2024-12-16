from dataclasses import dataclass
from pathlib import Path


@dataclass
class Bundle:
    root_path: Path
    entries: list[Path]

    def get_file_paths(self) -> list[Path]:
        resolved_entries = []
        for entry in self.entries:
            resolved_entries.append(self._apply_relative_path(self.root_path / "descriptor", entry))
        return resolved_entries

    def _apply_relative_path(self, path: Path, path_to_apply: Path) -> Path:
        print(path)
        print(path_to_apply)
        return (path / path_to_apply).resolve().relative_to(self.root_path)
