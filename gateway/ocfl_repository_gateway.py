import subprocess
from enum import Enum
from pathlib import Path
from subprocess import CalledProcessError

from gateway.bundle import Bundle
from gateway.coordinator import Coordinator
from gateway.exceptions import (
    NoStagedChangesError,
    StagedObjectAlreadyExistsError,
    ObjectDoesNotExistError,
    RepositoryGatewayError,
)
from gateway.object_file import ObjectFile
from gateway.repository_gateway import RepositoryGateway


class StorageLayout(Enum):
    FLAT_DIRECT = "0002-flat-direct-storage-layout"
    HASHED_N_TUPLE = "0004-hashed-n-tuple-storage-layout"


class OcflRepositoryGateway(RepositoryGateway):
    def __init__(
        self,
        storage_path: Path,
        storage_layout: StorageLayout = StorageLayout.FLAT_DIRECT,
    ):
        self.storage_path: Path = storage_path
        self.storage_layout: StorageLayout = storage_layout

    def create_repository(self) -> None:
        args: list[str | Path] = [
            "rocfl",
            "-r",
            self.storage_path,
            "init",
            "-l",
            self.storage_layout.value,
        ]
        try:
            subprocess.run(args, check=True, capture_output=True)
        except CalledProcessError as e:
            raise RepositoryGatewayError() from e

    def create_staged_object(self, id: str) -> None:
        args: list[str | Path] = ["rocfl", "-r", self.storage_path, "new", id]
        try:
            subprocess.run(args, check=True, capture_output=True)
        except CalledProcessError as e:
            already_exists_message = f"Illegal state: Cannot create object {id} because it already exists in staging"
            if already_exists_message in e.stderr.decode():
                raise StagedObjectAlreadyExistsError() from e
            raise RepositoryGatewayError() from e

    def _stage_object_file(self, id, source_path: Path, dest_path: Path) -> None:
        args: list[str | Path] = [
            "rocfl",
            "-r",
            self.storage_path,
            "cp",
            "-r",
            id,
            source_path,
            "--",
            dest_path,
        ]
        try:
            subprocess.run(args, check=True, capture_output=True)
        except CalledProcessError as e:
            raise RepositoryGatewayError() from e

    def stage_object_files(self, id: str, source_bundle: Bundle) -> None:
        if not self.has_object(id) and not self._has_staged_object(id):
            raise ObjectDoesNotExistError(
                f"No object or staged object found for id {id}"
            )
        package_root = source_bundle.root_path
        for file_path in source_bundle.entries:
            source_path = package_root / file_path
            self._stage_object_file(id=id, source_path=source_path, dest_path=file_path)

    def commit_object_changes(
        self, id: str, coordinator: Coordinator, message: str
    ) -> None:
        args: list[str | Path] = [
            "rocfl",
            "-r",
            self.storage_path,
            "commit",
            id,
            "-n",
            coordinator.username,
            "-a",
            f"mailto:{coordinator.email}",
            "-m",
            message,
        ]
        try:
            subprocess.run(args, check=True, capture_output=True)
        except CalledProcessError as e:
            no_staged_changes_message = f"No staged changes found for object {id}"
            if no_staged_changes_message in e.stderr.decode():
                raise NoStagedChangesError() from e
            raise RepositoryGatewayError() from e

    def purge_object(self, id: str) -> None:
        args: list[str | Path] = ["rocfl", "-r", self.storage_path, "purge", "-f", id]
        try:
            subprocess.run(args, check=True, capture_output=True)
        except CalledProcessError as e:
            raise RepositoryGatewayError() from e

    def has_object(self, id: str) -> bool:
        args: list[str | Path] = ["rocfl", "-r", self.storage_path, "info", id]
        try:
            subprocess.run(args, check=True, capture_output=True)
            return True
        except CalledProcessError as e:
            not_found_message = f"Not found: Object {id}"
            if not_found_message in e.stderr.decode():
                return False
            raise RepositoryGatewayError() from e

    def _has_staged_object(self, id: str):
        args: list[str | Path] = ["rocfl", "-r", self.storage_path, "status", id]
        try:
            subprocess.run(args, check=True, capture_output=True)
            return True
        except CalledProcessError as e:
            staged_version_not_found_message = (
                f"Not found: {id} does not have a staged version."
            )
            if staged_version_not_found_message in e.stderr.decode():
                return False
            raise RepositoryGatewayError() from e

    def get_object_files(
        self, id: str, include_staged: bool = False
    ) -> list[ObjectFile]:
        has_staged_object = self._has_staged_object(id)
        if not self.has_object(id) and not has_staged_object:
            raise ObjectDoesNotExistError(
                f"No object or staged object found for id {id}"
            )

        flags = "-ptS" if include_staged and has_staged_object else "-pt"
        args: list[str | Path] = ["rocfl", "-r", self.storage_path, "ls", flags, id]
        try:
            result = subprocess.run(args, check=True, capture_output=True)
        except CalledProcessError as e:
            raise RepositoryGatewayError() from e

        data = result.stdout.decode()
        if len(data) == 0:
            return []
        lines = data.strip().split("\n")
        rows = [line.split("\t") for line in lines]
        object_files = [
            ObjectFile(Path(row[0].strip()), Path(row[1].strip())) for row in rows
        ]
        return object_files
