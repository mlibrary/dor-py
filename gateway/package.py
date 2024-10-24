import os

from gateway.exceptions import NoContentException

class Package:

    def validate_path(self):
        if not os.path.exists(self.root_path):
            raise NoContentException(
                f"No content exists at path {self.root_path}"
            )

    def __init__(self, path: str):
        self.root_path: str = path

        self.validate_path()

    def get_file_paths(self) -> list[str]:
        paths = []
        for dirpath, _, filenames in os.walk(self.root_path):
            for filename in filenames:
                full_path = os.path.join(dirpath, filename)
                paths.append(os.path.relpath(full_path, self.root_path))
        return paths
