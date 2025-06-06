from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any
from unittest import TestCase

import pytest

from dor.providers.file_system_file_provider import FilesystemFileProvider
from gateway.bundle import Bundle
from gateway.coordinator import Coordinator
from gateway.enumerations import LogOrder
from gateway.exceptions import (
    NoStagedChangesError,
    ObjectDoesNotExistError,
    StagedObjectAlreadyExistsError,
)
from gateway.object_file import ObjectFile
from gateway.ocfl_repository_gateway import OcflRepositoryGateway, StorageLayout
from gateway.version_info import VersionInfo


class OcflRepositoryGatewayTest(TestCase):

    def setUp(self):
        test_deposit_path = Path("tests/fixtures/test_deposit")

        self.deposit_one_bundle = Bundle(
            root_path=test_deposit_path / "deposit_one",
            entries=[
                Path("A.txt"),
                Path("B/B.txt"),
                Path("C/D/D.txt"),
            ],
        )

        self.deposit_one_update_bundle = Bundle(
            root_path=test_deposit_path / "deposit_one_update",
            entries=[
                Path("E.txt"),
                Path("B/B.txt"),
            ],
        )

        self.storage_path = Path("tests/output/test_ocfl_repository_gateway")
        self.pres_storage = self.storage_path / "test_preservation_storage"
        self.extensions_path = self.pres_storage / "extensions" / "rocfl-staging"
        self.file_provider = FilesystemFileProvider()
        if self.storage_path.exists():
            self.file_provider.delete_dir_and_contents(self.storage_path)
        self.file_provider.create_directories(self.pres_storage)

        return super().setUp()

    @staticmethod
    def read_inventory(file_path: Path) -> dict[str, Any]:
        inventory_data = json.loads(file_path.read_text())
        return inventory_data

    @staticmethod
    def get_hashed_n_tuple_object_path(
        object_id: str, tuple_size: int = 3, num_tuples: int = 3
    ) -> Path:
        digest = hashlib.sha256(bytes(object_id, "utf-8")).hexdigest()
        n_tuple = tuple(
            digest[i: i + tuple_size]
            for i in range(0, tuple_size * num_tuples, tuple_size)
        )
        return Path().joinpath(*n_tuple, digest)

    def test_gateway_creates_repository(self):
        OcflRepositoryGateway(self.pres_storage).create_repository()

        namaste_path = self.pres_storage / "0=ocfl_1.1"
        self.assertTrue(namaste_path.exists())

    def test_gateway_creates_staged_object(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")

        object_path = OcflRepositoryGatewayTest.get_hashed_n_tuple_object_path(
            "deposit_one"
        )
        full_object_path = self.extensions_path / object_path
        self.assertTrue(full_object_path.exists())

        inventory_data = OcflRepositoryGatewayTest.read_inventory(
            full_object_path / "inventory.json"
        )
        self.assertEqual("deposit_one", inventory_data["id"])
        head_version = inventory_data["versions"][inventory_data["head"]]
        logical_paths = [
            path for paths in head_version["state"].values() for path in paths
        ]
        self.assertListEqual([], logical_paths)

    def test_gateway_raises_when_creating_staged_object_that_already_exists(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")

        with self.assertRaises(StagedObjectAlreadyExistsError):
            gateway.create_staged_object("deposit_one")

    def test_gateway_stages_changes(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.stage_object_files("deposit_one", self.deposit_one_bundle)

        self.assertTrue(self.extensions_path.exists())

        object_path = OcflRepositoryGatewayTest.get_hashed_n_tuple_object_path(
            "deposit_one"
        )
        full_object_path = self.extensions_path / object_path
        self.assertTrue(full_object_path.exists())

        inventory_data = OcflRepositoryGatewayTest.read_inventory(
            full_object_path / "inventory.json"
        )
        self.assertEqual("deposit_one", inventory_data["id"])
        head_version = inventory_data["versions"][inventory_data["head"]]
        logical_paths = [
            path for paths in head_version["state"].values() for path in paths
        ]
        self.assertSetEqual(set(["A.txt", "B/B.txt", "C/D/D.txt"]), set(logical_paths))

    def test_gateway_raises_when_staging_changes_for_object_that_does_not_exist(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        with self.assertRaises(ObjectDoesNotExistError):
            gateway.stage_object_files("deposit_one", self.deposit_one_bundle)

    def test_gateway_commits_changes(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.stage_object_files("deposit_one", self.deposit_one_bundle)
        gateway.commit_object_changes(
            "deposit_one",
            Coordinator("test", "test@example.edu"),
            "Adding first version!",
        )

        full_object_path = self.pres_storage / "deposit_one"
        self.assertTrue(full_object_path.exists())

        inventory_data = OcflRepositoryGatewayTest.read_inventory(
            full_object_path / "inventory.json"
        )
        self.assertEqual("deposit_one", inventory_data["id"])
        head_version = inventory_data["versions"][inventory_data["head"]]
        logical_paths = [
            path for paths in head_version["state"].values() for path in paths
        ]
        self.assertSetEqual(set(["A.txt", "B/B.txt", "C/D/D.txt"]), set(logical_paths))

        self.assertEqual("Adding first version!", head_version["message"])
        self.assertEqual("test", head_version["user"]["name"])
        self.assertEqual("mailto:test@example.edu", head_version["user"]["address"])

    def test_gateway_can_use_a_different_storage_layout_for_committed_object(self):
        gateway = OcflRepositoryGateway(
            storage_path=self.pres_storage, storage_layout=StorageLayout.HASHED_N_TUPLE
        )
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.stage_object_files("deposit_one", self.deposit_one_bundle)
        gateway.commit_object_changes(
            "deposit_one",
            Coordinator("test", "test@example.edu"),
            "Adding first version!",
        )

        object_path = OcflRepositoryGatewayTest.get_hashed_n_tuple_object_path(
            "deposit_one"
        )
        full_object_path = self.pres_storage / object_path
        self.assertTrue(full_object_path.exists())

    def test_gateway_raises_when_committing_an_object_that_is_not_staged(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()

        with self.assertRaises(NoStagedChangesError):
            gateway.commit_object_changes(
                "deposit_zero",
                Coordinator("test", "test@example.edu"),
                "Did I stage an object first?",
            )

    def test_gateway_commits_empty_object(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.commit_object_changes(
            "deposit_one",
            Coordinator("test", "test@example.edu"),
            "Adding empty version!",
        )

        full_object_path = self.pres_storage / "deposit_one"
        inventory_data = OcflRepositoryGatewayTest.read_inventory(
            full_object_path / "inventory.json"
        )
        self.assertEqual("deposit_one", inventory_data["id"])
        head_version = inventory_data["versions"][inventory_data["head"]]
        logical_paths = [
            path for paths in head_version["state"].values() for path in paths
        ]
        self.assertListEqual([], logical_paths)

    def test_gateway_purges_object(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.stage_object_files("deposit_one", self.deposit_one_bundle)
        gateway.commit_object_changes(
            "deposit_one",
            Coordinator("test", "test@example.edu"),
            "Adding first version!",
        )

        full_object_path = self.pres_storage / "deposit_one"
        self.assertTrue(full_object_path.exists())

        gateway.purge_object("deposit_one")

        self.assertFalse(full_object_path.exists())

    def test_gateway_does_not_raise_when_purging_object_that_does_not_exist(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.purge_object("deposit_zero")

    def test_gateway_indicates_it_does_not_have_an_object(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        result = gateway.has_object("deposit_zero")

        self.assertEqual(False, result)

    def test_gateway_indicates_it_does_not_have_an_object_once_staged(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        result = gateway.has_object("deposit_one")

        self.assertEqual(False, result)

    def test_gateway_indicates_it_does_have_an_object(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.stage_object_files("deposit_one", self.deposit_one_bundle)
        gateway.commit_object_changes(
            "deposit_one",
            Coordinator("test", "test@example.edu"),
            "Adding first version!",
        )
        result = gateway.has_object("deposit_one")

        self.assertEqual(True, result)

    def test_gateway_provides_object_files(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.stage_object_files("deposit_one", self.deposit_one_bundle)
        gateway.commit_object_changes(
            "deposit_one",
            Coordinator("test", "test@example.edu"),
            "Adding first version!",
        )

        gateway.stage_object_files("deposit_one", self.deposit_one_update_bundle)
        gateway.commit_object_changes(
            "deposit_one",
            Coordinator("test", "test@example.edu"),
            "Adding second version!",
        )

        object_files = gateway.get_object_files("deposit_one")
        prefix = self.pres_storage / "deposit_one"
        self.assertListEqual(
            [
                ObjectFile(Path("A.txt"), prefix.joinpath("v1", "content", "A.txt")),
                ObjectFile(
                    Path("B/B.txt"), prefix.joinpath("v2", "content", "B", "B.txt")
                ),
                ObjectFile(
                    Path("C/D/D.txt"),
                    prefix.joinpath("v1", "content", "C", "D", "D.txt"),
                ),
                ObjectFile(Path("E.txt"), prefix.joinpath("v2", "content", "E.txt")),
            ],
            object_files,
        )

    def test_gateway_provides_no_object_files_when_there_are_none(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.commit_object_changes(
            "deposit_one", Coordinator("test", "test@example.edu"), "Adding nothing!"
        )
        object_files = gateway.get_object_files("deposit_one")
        self.assertListEqual([], object_files)

    def test_gateway_provides_object_files_when_only_staged_ones_exist(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.stage_object_files("deposit_one", self.deposit_one_bundle)

        object_files = gateway.get_object_files("deposit_one", True)

        object_path = OcflRepositoryGatewayTest.get_hashed_n_tuple_object_path(
            "deposit_one"
        )
        prefix = self.extensions_path / object_path
        self.assertListEqual(
            [
                ObjectFile(Path("A.txt"), prefix.joinpath("v1", "content", "A.txt")),
                ObjectFile(
                    Path("B/B.txt"), prefix.joinpath("v1", "content", "B", "B.txt")
                ),
                ObjectFile(
                    Path("C/D/D.txt"),
                    prefix.joinpath("v1", "content", "C", "D", "D.txt"),
                ),
            ],
            object_files,
        )

    def test_gateway_provides_object_files_when_no_staged_ones_exist(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.stage_object_files("deposit_one", self.deposit_one_bundle)
        gateway.commit_object_changes(
            "deposit_one",
            Coordinator("test", "test@example.edu"),
            "Adding first version!",
        )

        object_files = gateway.get_object_files("deposit_one", True)
        prefix = self.pres_storage / "deposit_one"
        self.assertListEqual(
            [
                ObjectFile(Path("A.txt"), prefix.joinpath("v1", "content", "A.txt")),
                ObjectFile(
                    Path("B/B.txt"), prefix.joinpath("v1", "content", "B", "B.txt")
                ),
                ObjectFile(
                    Path("C/D/D.txt"),
                    prefix.joinpath("v1", "content", "C", "D", "D.txt"),
                ),
            ],
            object_files,
        )

    def test_gateway_provides_object_files_when_versioned_and_staged_files_exist(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.stage_object_files("deposit_one", self.deposit_one_bundle)
        gateway.commit_object_changes(
            "deposit_one",
            Coordinator("test", "test@example.edu"),
            "Adding first version!",
        )
        gateway.stage_object_files("deposit_one", self.deposit_one_update_bundle)

        object_files = gateway.get_object_files("deposit_one", True)

        storage_prefix = self.pres_storage / "deposit_one"
        object_path_in_staging = (
            OcflRepositoryGatewayTest.get_hashed_n_tuple_object_path("deposit_one")
        )
        staging_prefix = self.extensions_path / object_path_in_staging
        self.assertListEqual(
            [
                ObjectFile(
                    Path("A.txt"), storage_prefix.joinpath("v1", "content", "A.txt")
                ),
                ObjectFile(
                    Path("B/B.txt"),
                    staging_prefix.joinpath("v2", "content", "B", "B.txt"),
                ),
                ObjectFile(
                    Path("C/D/D.txt"),
                    storage_prefix.joinpath("v1", "content", "C", "D", "D.txt"),
                ),
                ObjectFile(
                    Path("E.txt"), staging_prefix.joinpath("v2", "content", "E.txt")
                ),
            ],
            object_files,
        )

    def test_gateway_raises_when_providing_files_for_object_that_does_not_exist(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()

        with self.assertRaises(ObjectDoesNotExistError):
            gateway.get_object_files("deposit_zero")

    def test_gateway_log_raises_for_object_that_does_not_exist(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()

        with pytest.raises(ObjectDoesNotExistError):
            gateway.log("deposit_one")

    def test_gateway_log_raises_for_a_staged_object(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.stage_object_files("deposit_one", self.deposit_one_bundle)

        with pytest.raises(ObjectDoesNotExistError):
            gateway.log("deposit_one")

    def test_gateway_log_committed_object(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.stage_object_files("deposit_one", self.deposit_one_bundle)
        date = datetime.now(timezone.utc).astimezone()
        rfc7231ish = date.strftime("%a, %d %b %G %T +0000")
        gateway.commit_object_changes(
            "deposit_one",
            Coordinator("test", "test@example.edu"),
            "Adding first version!",
            date,
        )

        log = gateway.log("deposit_one")
        assert len(log) == 1
        assert log[0] == VersionInfo(version=1, author='test <mailto:test@example.edu>',
                                     date=rfc7231ish, message='Adding first version!')

    def test_gateway_log_committed_staged_object(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.stage_object_files("deposit_one", self.deposit_one_bundle)
        gateway.commit_object_changes(
            "deposit_one",
            Coordinator("test", "test@example.edu"),
            "Adding first version!",
        )
        gateway.stage_object_files("deposit_one", self.deposit_one_update_bundle)

        log = gateway.log("deposit_one")
        assert len(log) == 1

    def test_gateway_log_default_descending_order(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.stage_object_files("deposit_one", self.deposit_one_bundle)
        gateway.commit_object_changes(
            "deposit_one",
            Coordinator("test", "test@example.edu"),
            "Adding first version!",
        )
        gateway.stage_object_files("deposit_one", self.deposit_one_update_bundle)
        gateway.commit_object_changes(
            "deposit_one",
            Coordinator("test", "test@example.edu"),
            "Adding second version!",
        )

        log = gateway.log("deposit_one")
        assert log[0].version == 2
        assert log[1].version == 1

    def test_gateway_log_optional_ascending_order(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.stage_object_files("deposit_one", self.deposit_one_bundle)
        gateway.commit_object_changes(
            "deposit_one",
            Coordinator("test", "test@example.edu"),
            "Adding first version!",
        )
        gateway.stage_object_files("deposit_one", self.deposit_one_update_bundle)
        gateway.commit_object_changes(
            "deposit_one",
            Coordinator("test", "test@example.edu"),
            "Adding second version!",
        )

        log = gateway.log("deposit_one", order=LogOrder.ascending)
        assert log[0].version == 1
        assert log[1].version == 2
