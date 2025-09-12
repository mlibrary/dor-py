import os
from datetime import datetime, UTC
from pathlib import Path

from ocfl import Object, StorageRoot, VersionMetadata

from gateway.coordinator import Coordinator
from gateway.exceptions import ObjectAlreadyExistsError, ObjectDoesNotExistError
from gateway.object_file import ObjectFile
from gateway.version_info import VersionInfo


class OcflPyRepositoryGateway():

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_root = StorageRoot(
            root=str(self.storage_path),
            layout_name="flat-direct"
        )

    def create_repository(self) -> None:
        self.storage_root.initialize()

    def has_object(self, id: str) -> bool:
        for _, identifier in self.storage_root.list_objects():
            if identifier == id:
                return True
        return False

    def _get_object_path(self, id: str) -> Path:
        return self.storage_path / self.storage_root.object_path(id)

    def create_new_object(
        self,
        id: str,
        src_path: Path,
        coordinator: Coordinator,
        message: str,
        timestamp: datetime | None = None
    ) -> None:
        if self.has_object(id):
            raise ObjectAlreadyExistsError

        obj = Object(identifier=id)
        
        version_metadata = VersionMetadata(
            created=timestamp.isoformat() if timestamp else datetime.now(tz=UTC).isoformat(),
            message=message,
            name=coordinator.username,
            address="mailto:" + coordinator.email
        )

        obj.create(
            srcdir=str(src_path),
            metadata=version_metadata,
            objdir=str(self._get_object_path(id))
        )

    def update_object(
        self,
        id: str,
        src_path: Path,
        coordinator: Coordinator,
        message: str,
        timestamp: datetime | None = None
    ) -> None:
        if not self.has_object(id):
            raise ObjectDoesNotExistError()

        obj = Object(identifier=id)
        version_metadata = VersionMetadata(
            created=timestamp.isoformat() if timestamp else datetime.now(tz=UTC).isoformat(),
            message=message,
            name=coordinator.username,
            address="mailto:" + coordinator.email
        )
        new_version = obj.start_new_version(
            objdir=str(self._get_object_path(id)),
            srcdir=str(src_path),
            metadata=version_metadata,
            carry_content_forward=True
        )
        for source_file_path in sorted(new_version.src_fs.walk.files()):
            norm_source_file_path = os.path.relpath(source_file_path, "/")
            if norm_source_file_path in new_version.inventory.current_version.logical_paths:
                new_version.delete(norm_source_file_path)
            new_version.add(norm_source_file_path, norm_source_file_path, src_path_has_prefix=False)
        obj.write_new_version(new_version)

    def get_object_files(self, id: str) -> list[ObjectFile]:
        if not self.has_object(id):
            raise ObjectDoesNotExistError()

        obj_path = self._get_object_path(id)
        obj = Object(path=str(obj_path))
        inventory = obj.parse_inventory()
        inventory_data = inventory.data
        manifest = inventory_data["manifest"]
        head_version = inventory_data["versions"][inventory_data["head"]]
        head_state = head_version["state"]

        object_files: list[ObjectFile] = []
        for digest, logical_paths in head_state.items():
            for logical_path in logical_paths:
                object_files.append(
                    ObjectFile(
                        logical_path=Path(logical_path),
                        literal_path=obj_path / manifest[digest][0]  # dedupe assumption?
                    )
                )

        return object_files

    def log(self, id: str, reversed: bool = True) -> list[VersionInfo]:
        obj_path = self._get_object_path(id)
        obj = Object(path=str(obj_path))
        inventory = obj.parse_inventory()
        version_infos = []
        for version in inventory.versions():
            version_infos.append(VersionInfo(
                version=version.number,
                author=f"{version.user_name} <{version.user_address}>",
                date=datetime.fromisoformat(version.created),
                message=version.message
            ))
        if reversed:
            version_infos = sorted(version_infos, key=lambda x: x.version, reverse=True)

        return version_infos

    def purge_object(self, id: str) -> None:
        self.storage_root.open_root_fs()
        object_rel_path = self.storage_root.object_path(id)
        self.storage_root.root_fs.removetree(str(object_rel_path))

    # def create_staged_object(self, id: str) -> None:
    #     pass

    # def stage_object_files(self, id: str, source_bundle: Bundle) -> None:
    #     pass

    # def commit_object_changes(
    #     self,
    #     id: str,
    #     coordinator: Coordinator,
    #     message: str,
    #     date: datetime = datetime.now(timezone.utc).astimezone()
    # ) -> None:
    #     pass

