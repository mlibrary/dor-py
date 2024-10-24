import os

import gateway.deposit_directory
from gateway.exceptions import NoContentException

class Package:

    def get_root_path(self) -> str:
        return self.deposit_dir.resolve(self.path)

    def validate_path(self) -> None:
        root_path = self.get_root_path()
        if not os.path.exists(root_path):
            raise NoContentException(
                f"No content exists at path {root_path}"
            )

    def __init__(self, deposit_dir: 'gateway.deposit_directory.DepositDirectory', path: str):
        self.deposit_dir: 'gateway.deposit_directory.DepositDirectory' = deposit_dir
        self.path: str = path

        self.validate_path()

    def get_file_paths(self) -> list[str]:
        root_path = self.get_root_path()
        paths = []
        for dirpath, _, filenames in os.walk(root_path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                paths.append(os.path.relpath(full_path, root_path))
        return paths
