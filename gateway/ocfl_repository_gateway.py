import logging
import os
import subprocess

from gateway.coordinator import Coordinator
from gateway.exceptions import (
    ObjectAlreadyExistsException,
    ObjectDoesNotExistException,
    ObjectNotStagedException
)
from gateway.object_file import ObjectFile
from gateway.package import Package
from gateway.repository_gateway import RepositoryGateway

logger = logging.getLogger(__file__)

class OcflRepositoryGateway(RepositoryGateway):
    storage_layout = "0002-flat-direct-storage-layout"

    def __init__(self, storage_path: str):
        self.storage_path = storage_path

    def create_repository(self) -> None:
        args = [
            "rocfl", "-r", self.storage_path, "init",
            "-l", self.storage_layout
        ]
        subprocess.run(args, check=True)

    def create_staged_object(self, id: str) -> None:
        args = ["rocfl", "-r", self.storage_path, "new", id]
        try:
            subprocess.run(args, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            already_exists_message = (
                f"Illegal state: Cannot create object {id} because it already exists in staging"
            )
            if already_exists_message in e.stderr.decode():
                raise ObjectAlreadyExistsException()
            raise e

    def stage_object_files(self, id: str, source_package: Package) -> None:
        command = " ".join([
            "rocfl", "-r", self.storage_path,
            "cp", "-r", id, os.path.join(source_package.get_root_path(), "*"), "--", "/"
        ])
        try:
            subprocess.run(command, check=True, shell=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            not_found_message = f"Not found: Object {id}"
            if not_found_message in e.stderr.decode():
                raise ObjectDoesNotExistException()
            raise e

    def commit_object_changes(
        self,
        id: str,
        coordinator: Coordinator,
        message: str
    ) -> None:
        args = [
            "rocfl", "-r", self.storage_path, "commit", id,
            "-n", coordinator.username, "-a", f"mailto:{coordinator.email}",
            "-m", message
        ]
        try:
            subprocess.run(args, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            no_staged_changes_message = f"No staged changes found for object {id}"
            if no_staged_changes_message in e.stderr.decode():
                raise ObjectNotStagedException()
            raise e

    def purge_object(self, id: str) -> None:
        args = ["rocfl", "-r", self.storage_path, "purge", "-f", id]
        subprocess.run(args, check=True)

    def has_object(self, id: str) -> bool:
        args = ["rocfl", "-r", self.storage_path, "info", id]
        try:
            subprocess.run(args, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            not_found_message = f"Not found: Object {id}"
            if not_found_message in e.stderr.decode():
                return False
            raise e

    def get_file_paths(self, id: str) -> list[str]:
        args = ["rocfl", "-r", self.storage_path, "ls", id]
        result = subprocess.run(args, check=True, capture_output=True)
        data = result.stdout.decode()
        return data.split()

    def has_staged_object_changes(self, id: str):
        args = ["rocfl", "-r", self.storage_path, "status", id]
        try:
            subprocess.run(args, check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def get_object_files(self, id: str, include_staged: bool = False) -> list[ObjectFile]:
        object_has_staged_changes = self.has_staged_object_changes(id)
        if not self.has_object(id) and not object_has_staged_changes:
            raise ObjectDoesNotExistException(
                f"No object or staged changes found for id {id}"
            )

        flags = "-ptS" if include_staged and object_has_staged_changes else "-pt"
        args = ["rocfl", "-r", self.storage_path, "ls", flags, id]
        result = subprocess.run(args, check=True, capture_output=True)
        data = result.stdout.decode()
        if len(data) == 0:
            return []
        lines = data.strip().split("\n")
        rows = [line.split("\t") for line in lines]
        object_files = [ObjectFile(row[0].strip(), row[1].strip()) for row in rows]
        return object_files
