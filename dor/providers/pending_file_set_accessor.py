import os
from enum import Enum
from pathlib import Path

from dor.providers.file_provider import FileProvider


class PendingFileSetAccessorError(Exception):

    def __init__(self, message: str):
        super().__init__(message)

        self.message = message


class PendingFileSetStatus(Enum):
    NOT_FOUND = "NotFound"
    UNDEFINED = "Undefined"
    UNKNOWN = "Unknown"
    PROCESSING = "Processing"
    DEFECTIVE = "Defective"
    FINISHED = "Finished"


class PendingFileSetAccessor:

    @classmethod
    def sort_job_index_key(cls, path: Path):
        try:
            index = int(os.path.basename(path))
            return index
        except ValueError:
            return -1

    def __init__(self, file_provider: FileProvider, path: Path):
        self.file_provider = file_provider
        self.path = path

    def path(self) -> Path:
        return self.path

    def count(self) -> int:
        files = dirs = 0
        for entry in self.path.iterdir():
            if entry.is_dir():
                dirs += 1
            elif entry.is_file():
                files += 1
        return dirs

    def status(self, file_set_id: str) -> PendingFileSetStatus:
        if not (self.path / file_set_id).exists():
            return PendingFileSetStatus.NOT_FOUND

        file_set_job_indecies = [
            entry.name for entry in sorted((self.path / file_set_id).iterdir(), key=self.sort_job_index_key, reverse=True)
            if entry.is_dir()
        ]

        if len(file_set_job_indecies) == 0:
            return PendingFileSetStatus.UNDEFINED

        latest_file_set_job_index_path = self.path / file_set_id / file_set_job_indecies[0]

        if (latest_file_set_job_index_path / ".defective").exists():
            return PendingFileSetStatus.DEFECTIVE

        if (latest_file_set_job_index_path / ".finished").exists():
            return PendingFileSetStatus.FINISHED

        if (latest_file_set_job_index_path / ".processing").exists():
            return PendingFileSetStatus.PROCESSING

        return PendingFileSetStatus.UNKNOWN

    def push(self, file_set_id: str, destination_path: Path) -> None:
        if not self.status(file_set_id) == PendingFileSetStatus.FINISHED:
            raise PendingFileSetAccessorError(
                f"Expected pending file set \"{file_set_id}\" to be finished, but got {self.status(file_set_id)}"
            )

        file_set_directories = [
            entry.name for entry in sorted((self.path / file_set_id).iterdir(), key=self.sort_job_index_key, reverse=True)
            if entry.is_dir()
        ]

        self.file_provider.clone_directory_structure(
            self.path / file_set_id / file_set_directories[0] / "build" / file_set_id,
            destination_path / file_set_id
        )
