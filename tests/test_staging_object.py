from datetime import datetime, UTC
from pathlib import Path
from unittest import TestCase

from ocfl import Object, VersionMetadata, StorageRoot

from dor.providers.file_system_file_provider import FilesystemFileProvider
from gateway.staging_object import StagingObject


class StagingObjectTest(TestCase):

    def setUp(self):
        test_deposit_path = Path("tests/fixtures/test_deposit")

        self.deposit_one_path = test_deposit_path / "deposit_one"
        self.deposit_one_update_path = test_deposit_path / "deposit_one_update"
        self.empty_deposit_path = test_deposit_path / "empty_deposit"

        self.storage_path = Path("tests/output/test_staging_object")
        self.pres_storage = self.storage_path / "test_preservation_storage"
        self.staging_path = self.pres_storage / "extensions" / "staging"

        self.file_provider = FilesystemFileProvider()
        if self.storage_path.exists():
            self.file_provider.delete_dir_and_contents(self.storage_path)
        self.file_provider.create_directories(self.storage_path)

        self.storage_root = StorageRoot(str(self.pres_storage), layout_name="flat-direct")
        self.storage_root.initialize()

        if self.staging_path.exists():
            self.file_provider.delete_dir_and_contents(self.staging_path)
        self.file_provider.create_directories(self.staging_path)


        return super().setUp()

    def test_staging_object_creates_staged_object(self):
        object_path = self.pres_storage / self.storage_root.object_path("deposit_one")
        obj = Object(identifier="deposit_one")
        staging_obj = StagingObject(
            obj=obj,
            object_path=object_path,
            staging_path=self.staging_path
        )

        staging_obj.stage_changes(src_dir=self.deposit_one_path)

        deposit_path = self.staging_path / "deposit_one"
        self.assertTrue(deposit_path.exists())

    def test_staging_object_commits_staged_object(self):
        object_path = self.pres_storage / self.storage_root.object_path("deposit_one")
        obj = Object(identifier="deposit_one")
        staging_obj = StagingObject(
            obj=obj,
            object_path=object_path,
            staging_path=self.staging_path
        )

        now = datetime.now(tz=UTC).isoformat()
        version_metadata = VersionMetadata(
            created=now,
            message="Initial version",
            name="test",
            address="mailto:test@example.edu"
        )

        staging_obj.stage_changes(src_dir=self.deposit_one_path)
        staging_obj.commit_changes(version_metadata)

        committed_object_path = self.pres_storage / "deposit_one"
        self.assertTrue(committed_object_path.exists())


    def test_staging_object_commits_staged_object_on_top_of_existing_object(self):
        pass
