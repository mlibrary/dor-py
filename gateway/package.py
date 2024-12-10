from pathlib import Path

import gateway.deposit_directory
from gateway.exceptions import NoContentError

class Package:

    def get_root_path(self) -> Path:
        return self.deposit_dir.resolve(self.path)

    def validate_path(self) -> None:
        root_path = self.get_root_path()
        if not root_path.exists():
            raise NoContentError(f"No content exists at path {root_path}")

    def __init__(self, deposit_dir: 'gateway.deposit_directory.DepositDirectory', path: Path):
        self.deposit_dir: 'gateway.deposit_directory.DepositDirectory' = deposit_dir
        self.path: Path = path

        self.validate_path()

    def get_file_paths(self) -> list[Path]:
        root_path = self.get_root_path()

        paths = []
        for dirpath, _, filenames in root_path.walk():
            for filename in filenames:
                full_path = dirpath / filename
                paths.append(full_path.relative_to(root_path))
        return paths
