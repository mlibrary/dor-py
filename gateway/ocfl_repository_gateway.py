import subprocess

from gateway.coordinator import Coordinator
from gateway.package import Package
from gateway.repository_gateway import RepositoryGateway

class OcflRepositoryGateway(RepositoryGateway):
    
    def __init__(self, storage_path: str):
        self.storage_path = storage_path

    def create_repository(self):
        subprocess.run(["rocfl", "-r", self.storage_path, "init"], check=True)

    def create_empty_object(self, id: str) -> None:
        subprocess.run(["rocfl", "-r", self.storage_path, "new", id], check=True)

    def stage_object_files(self, id: str, source_package: Package):
        args = [
            "rocfl", "-r", self.storage_path,
             "cp", "-r", id, source_package.get_root_path(), "--", "/"
        ]
        subprocess.run(args, check=True)

    def commit_object_changes(
        self,
        id: str,
        coordinator: Coordinator,
        message: str
    ):
        args = [
            "rocfl", "-r", self.storage_path, "commit", id,
            "-n", coordinator.username, "-a", f"mailto:{coordinator.email}",
            "-m", message
        ]
        subprocess.run(args, check=True)

    def read_object(self, id: str, output_path: str):
        raise NotImplementedError()

    def purge_object(self, id: str):
        raise NotImplementedError()

    def delete_object_file(
        self,
        id: str,
        file_path: str,
        coordinator: Coordinator,
        message: str
    ):
        raise NotImplementedError()

    def has_object(self, id: str):
        raise NotImplementedError()

    def get_file_paths(self, id: str):
        raise NotImplementedError()

    def get_storage_relative_file_paths(self, id: str):
        raise NotImplementedError()
