import os
import hashlib
import shutil
from datetime import datetime, UTC
from pathlib import Path

from ocfl import Object, StorageRoot, VersionMetadata

from gateway.bundle import Bundle
from gateway.coordinator import Coordinator
from gateway.exceptions import (
    ObjectAlreadyExistsError,
    ObjectDoesNotExistError,
    NoStagedChangesError,
    StagedObjectAlreadyExistsError,
)
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
        # Initialize the Mutable Head (0005) extension area
        ext_dir = self.storage_path / "extensions" / "0005-mutable-head"
        ext_dir.mkdir(parents=True, exist_ok=True)

    def has_object(self, id: str) -> bool:
        obj_path = self._get_object_path(id)
        # Consider the object present if its inventory exists at the expected path
        return (obj_path / "inventory.json").exists()

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

    def get_object_files(self, id: str, include_staged: bool = False) -> list[ObjectFile]:
        """
        List object files at HEAD. If include_staged is True and a staged version exists
        for the object, overlay staged files on top of committed HEAD for the result.
        """
        has_committed = self.has_object(id)
        has_staged = self._has_staged_object(id)

        if not has_committed and not (include_staged and has_staged):
            # Neither committed object nor staged when requested
            raise ObjectDoesNotExistError()

        mapping: dict[Path, Path] = {}

        if has_committed:
            obj_path = self._get_object_path(id)
            obj = Object(path=str(obj_path))
            inventory = obj.parse_inventory()
            inventory_data = inventory.data
            manifest: dict[str, list[str]] = inventory_data["manifest"]
            head_version = inventory_data["versions"][inventory_data["head"]]
            head_state: dict[str, list[str]] = head_version["state"]

            for digest, logical_paths in head_state.items():
                manifest_paths = manifest.get(digest, [])
                for logical_path in logical_paths:
                    lp_norm = str(logical_path).lstrip("/").replace("\\", "/")
                    # Find all manifest entries that map to this logical path
                    candidates: list[tuple[int, str]] = []
                    for content_rel in manifest_paths:
                        norm_rel = str(content_rel).replace("\\", "/")
                        if norm_rel.endswith("/" + lp_norm):
                            # Extract version number from 'vN/content/...'
                            try:
                                # Expect the path to start with vN/
                                parts = norm_rel.split("/", 2)
                                v_str = parts[0]
                                if v_str.startswith("v"):
                                    v_num = int(v_str[1:])
                                    candidates.append((v_num, norm_rel))
                            except Exception:
                                # If parsing fails, still allow as a candidate with a large version number
                                candidates.append((10**9, norm_rel))
                    chosen_rel: str | None = None
                    if candidates:
                        # Choose the earliest version that introduced this content for this logical path
                        candidates.sort(key=lambda t: t[0])
                        chosen_rel = candidates[0][1]
                    elif manifest_paths:
                        # Fallback to first entry if nothing matches suffix (defensive)
                        chosen_rel = str(manifest_paths[0])
                    if chosen_rel is not None:
                        mapping[Path(logical_path)] = obj_path / chosen_rel

        if include_staged and has_staged:
            # Overlay staged files
            staging_content_dir = self._get_staging_version_dir(id)
            if staging_content_dir.exists():
                for p in staging_content_dir.rglob("*"):
                    if p.is_file():
                        rel = p.relative_to(staging_content_dir)
                        mapping[Path(str(rel))] = p

        # Return sorted by logical path for deterministic output
        object_files = [ObjectFile(logical_path=k, literal_path=v) for k, v in sorted(mapping.items(), key=lambda kv: str(kv[0]))]
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

    # ----- Mutable Head (0005) extension helpers and operations -----

    def _object_hashed_path(self, object_id: str, tuple_size: int = 3, num_tuples: int = 3) -> Path:
        """
        Generate a hashed-n-tuple path for an object using sha256.
        Mirrors common practice to avoid large fanout in a single directory.
        """
        digest = hashlib.sha256(object_id.encode("utf-8")).hexdigest()
        pieces = [digest[i:i + tuple_size] for i in range(0, tuple_size * num_tuples, tuple_size)]
        return Path(*pieces, digest)

    def _get_staging_base_path(self) -> Path:
        return self.storage_path / "extensions" / "0005-mutable-head"

    def _get_staging_version_dir(self, id: str) -> Path:
        """
        Determine the staged version directory path for the next version.
        v1 for new objects; otherwise v{head+1} for existing objects.
        The staged content is placed under vN/content, analogous to OCFL object layout.
        """
        # Ensure extension base exists
        base = self._get_staging_base_path()
        base.mkdir(parents=True, exist_ok=True)

        # Use a hashed path for the staged object
        obj_stage_root = base / self._object_hashed_path(id)
        obj_stage_root.mkdir(parents=True, exist_ok=True)

        # Determine next version number (1 if new object)
        if self.has_object(id):
            obj = Object(path=str(self._get_object_path(id)))
            inv = obj.parse_inventory()
            head_num = int(inv.data["head"][1:])  # 'vN' -> N
            next_version = head_num + 1
        else:
            next_version = 1

        return obj_stage_root / f"v{next_version}" / "content"

    def _has_staged_object(self, id: str) -> bool:
        base = self._get_staging_base_path()
        obj_stage_root = base / self._object_hashed_path(id)
        if not obj_stage_root.exists():
            return False
        # Check if any v*/content directory exists with content or as a marker
        for child in obj_stage_root.iterdir():
            if child.is_dir() and child.name.startswith("v"):
                return True
        return False

    def create_staged_object(self, id: str) -> None:
        """
        Start a staged mutable head for the object. For new objects, this prepares v1/content.
        For existing objects, this prepares v{head+1}/content. It raises if a staged version already exists.
        """
        if self._has_staged_object(id):
            raise StagedObjectAlreadyExistsError()

        staging_content_dir = self._get_staging_version_dir(id)
        staging_content_dir.mkdir(parents=True, exist_ok=True)

    def _copy_into(self, source_path: Path, dest_path: Path) -> None:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, dest_path)

    def stage_object_files(self, id: str, source_bundle: Bundle) -> None:
        """
        Copy files from the provided bundle into the staged content directory.
        Raises ObjectDoesNotExistError if there is neither a committed object nor a staged one.
        """
        if not self.has_object(id) and not self._has_staged_object(id):
            raise ObjectDoesNotExistError(f"No object or staged object found for id {id}")

        # Ensure we have a staged version directory (must be explicitly created)
        if not self._has_staged_object(id):
            # For explicitness: require create_staged_object before staging
            raise ObjectDoesNotExistError(f"No staged object exists for id {id}; call create_staged_object first")

        staging_content_dir = self._get_staging_version_dir(id)
        for rel_path in source_bundle.entries:
            src_path = source_bundle.root_path / rel_path
            dest_path = staging_content_dir / rel_path
            self._copy_into(src_path, dest_path)

    def commit_object_changes(
        self,
        id: str,
        coordinator: Coordinator,
        message: str,
        date: datetime | None = None
    ) -> None:
        """
        Commit staged changes as a new immutable version using ocfl-py.
        Raises NoStagedChangesError if no staged changes exist.
        """
        if not self._has_staged_object(id):
            raise NoStagedChangesError()

        staging_content_dir = self._get_staging_version_dir(id)
        # It's possible that the staged version exists but contains no files (empty commit)
        has_any_files = any(
            p.is_file() for p in staging_content_dir.rglob("*")
        ) if staging_content_dir.exists() else False

        created = date.isoformat() if date else datetime.now(tz=UTC).isoformat()
        if self.has_object(id):
            # Update existing object
            obj = Object(identifier=id)
            version_metadata = VersionMetadata(
                created=created,
                message=message,
                name=coordinator.username,
                address="mailto:" + coordinator.email,
            )
            new_version = obj.start_new_version(
                objdir=str(self._get_object_path(id)),
                srcdir=str(staging_content_dir) if staging_content_dir.exists() else None,
                metadata=version_metadata,
                carry_content_forward=True,
            )
            if has_any_files:
                for source_file_path in sorted(new_version.src_fs.walk.files()):
                    norm_source_file_path = os.path.relpath(source_file_path, "/")
                    if norm_source_file_path in new_version.inventory.current_version.logical_paths:
                        new_version.delete(norm_source_file_path)
                    new_version.add(norm_source_file_path, norm_source_file_path, src_path_has_prefix=False)
            obj.write_new_version(new_version)
        else:
            # Create new object
            obj = Object(identifier=id)
            version_metadata = VersionMetadata(
                created=created,
                message=message,
                name=coordinator.username,
                address="mailto:" + coordinator.email,
            )
            # For empty object, create from an empty dir
            srcdir = str(staging_content_dir) if staging_content_dir.exists() else None
            empty_dir = None
            if not has_any_files:
                # Create a temporary empty directory under the staging root to allow creation
                empty_dir = staging_content_dir if staging_content_dir.exists() else self._get_staging_base_path() / "_empty"
                empty_dir.mkdir(parents=True, exist_ok=True)
                srcdir = str(empty_dir)
            obj.create(
                srcdir=srcdir,
                metadata=version_metadata,
                objdir=str(self._get_object_path(id)),
            )
            # Clean temporary empty dir if we created one
            if empty_dir is not None and empty_dir.exists():
                try:
                    shutil.rmtree(empty_dir)
                except Exception:
                    pass

        # Cleanup the staged content after successful commit
        try:
            stage_root = (self._get_staging_base_path() / self._object_hashed_path(id))
            if stage_root.exists():
                shutil.rmtree(stage_root)
        except Exception:
            # Non-fatal cleanup failure
            pass

