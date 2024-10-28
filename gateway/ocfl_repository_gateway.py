import logging
import os
import subprocess

from gateway.coordinator import Coordinator
from gateway.exceptions import ObjectDoesNotExistException
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
        subprocess.run(["rocfl", "-r", self.storage_path, "new", id], check=True)

    def stage_object_files(self, id: str, source_package: Package) -> None:
        command = " ".join([
            "rocfl", "-r", self.storage_path,
            "cp", "-r", id, os.path.join(source_package.get_root_path(), "*"), "--", "/"
        ])
        subprocess.run(command, check=True, shell=True)

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
        subprocess.run(args, check=True)

    def purge_object(self, id: str) -> None:
        args = ["rocfl", "-r", self.storage_path, "purge", "-f", id]
        subprocess.run(args, check=True)

    def has_object(self, id: str) -> bool:
        args = ["rocfl", "-r", self.storage_path, "info", id]
        try:
            subprocess.run(args, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

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
        if not self.has_object(id) and not self.has_staged_object_changes(id):
            raise ObjectDoesNotExistException()

        flags = "-ptS" if include_staged and self.has_staged_object_changes(id) else "-pt"
        args = ["rocfl", "-r", self.storage_path, "ls", flags, id]
        try:
            result = subprocess.run(args, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            logger.error(e)
            return []
        data = result.stdout.decode()
        if len(data) == 0:
            return []
        lines = data.strip().split("\n")
        rows = [line.split("\t") for line in lines]
        object_files = [ObjectFile(row[0].strip(), row[1].strip()) for row in rows]
        return object_files
