from pathlib import Path

from ocfl import Object, VersionMetadata


class StagingObject():

    def __init__(self, obj: Object, object_path: Path, staging_path: Path):
        self.obj = obj
        self.object_path = object_path
        self.staging_path = staging_path
        self.staged_object_path = self.staging_path / self.obj.id

    def stage_changes(self, src_dir: Path) -> None:
        self.staged_object_path.mkdir()
        self.staged_obj = Object(identifier=self.obj.id)
        self.staged_obj.create(
            srcdir=str(src_dir),
            objdir=str(self.staged_object_path)
        )

    def commit_changes(self, version_metadata: VersionMetadata) -> None:
        if not self.staged_obj:
            raise Exception()
        
        self.obj.create(
            srcdir=str(self.staged_object_path / "v1" / "content"),
            metadata=version_metadata,
            objdir=str(self.object_path)
        )