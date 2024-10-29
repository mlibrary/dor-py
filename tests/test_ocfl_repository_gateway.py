import hashlib
import json
import os
import shutil
from typing import Any
from unittest import TestCase

from gateway.coordinator import Coordinator
from gateway.deposit_directory import DepositDirectory
from gateway.exceptions import (
    ObjectAlreadyExistsException,
    ObjectDoesNotExistException,
    ObjectNotStagedException
)
from gateway.object_file import ObjectFile
from gateway.ocfl_repository_gateway import OcflRepositoryGateway

class OcflRepositoryGatewayTest(TestCase):

    def setUp(self):
        test_deposit_path = os.path.join("tests", "fixtures", "test_deposit")
        self.deposit_dir = DepositDirectory(test_deposit_path)
        
        self.storage_path = os.path.join("tests", "test_storage")
        self.pres_storage = os.path.join(self.storage_path, "test_preservation_storage")
        self.extensions_path = os.path.join(self.pres_storage, "extensions", "rocfl-staging")

        if os.path.exists(self.storage_path):
            shutil.rmtree(self.storage_path)
        os.makedirs(self.pres_storage)

        return super().setUp()

    @staticmethod
    def read_inventory(file_path: str) -> dict[str, Any]:
        with open(file_path, "r") as file:
            inventory_data = json.loads(file.read())
        return inventory_data

    @staticmethod
    def get_hashed_n_tuple_object_path(
        object_id: str, tuple_size: int = 3, num_tuples: int = 3
    ) -> str:
        digest = hashlib.sha256(bytes(object_id, 'utf-8')).hexdigest()
        n_tuple = tuple(
            digest[i:i + tuple_size]
            for i in range(0, tuple_size * num_tuples, tuple_size)
        )
        return os.path.join(*n_tuple, digest)

    def test_gateway_creates_repository(self):
        OcflRepositoryGateway(self.pres_storage).create_repository()

        # Check for namaste file
        namaste_path = os.path.join(self.pres_storage, "0=ocfl_1.1")
        self.assertTrue(os.path.exists(namaste_path))

    def test_gateway_creates_staged_object(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")

        object_path = OcflRepositoryGatewayTest.get_hashed_n_tuple_object_path("deposit_one")
        full_object_path = os.path.join(self.extensions_path, object_path)
        self.assertTrue(os.path.exists(full_object_path))

        inventory_path = os.path.join(full_object_path, "inventory.json")
        inventory_data = OcflRepositoryGatewayTest.read_inventory(inventory_path)
        self.assertEqual("deposit_one", inventory_data["id"])
        head_version = inventory_data["versions"][inventory_data["head"]]
        logical_paths = [path for paths in head_version["state"].values() for path in paths]
        self.assertListEqual([], logical_paths)

    def test_gateway_raises_when_creating_staged_object_that_already_exists(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")

        with self.assertRaises(ObjectAlreadyExistsException):
            gateway.create_staged_object("deposit_one")

    def test_gateway_stages_changes(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        package = self.deposit_dir.get_package("deposit_one")
        gateway.stage_object_files("deposit_one", package)

        # Check for changes under extensions
        self.assertTrue(os.path.exists(self.extensions_path))

        object_path = OcflRepositoryGatewayTest.get_hashed_n_tuple_object_path("deposit_one")
        full_object_path = os.path.join(self.extensions_path, object_path)
        self.assertTrue(os.path.exists(full_object_path))

        inventory_path = os.path.join(full_object_path, "inventory.json")
        inventory_data = OcflRepositoryGatewayTest.read_inventory(inventory_path)
        self.assertEqual("deposit_one", inventory_data["id"])
        head_version = inventory_data["versions"][inventory_data["head"]]
        logical_paths = [path for paths in head_version["state"].values() for path in paths]
        self.assertSetEqual(
            set(["A.txt", "B/B.txt", "C/D/D.txt"]), set(logical_paths)
        )

    def test_gateway_raises_when_staging_changes_for_object_that_does_not_exist(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        package = self.deposit_dir.get_package("deposit_one")
        with self.assertRaises(ObjectDoesNotExistException):
            gateway.stage_object_files("deposit_one", package)

    def test_gateway_commits_changes(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        package = self.deposit_dir.get_package("deposit_one")
        gateway.stage_object_files("deposit_one", package)
        gateway.commit_object_changes(
            "deposit_one", Coordinator("test", "test@example.edu"), "Adding first version!"
        )

        # Check for changes in storage root
        full_object_path = os.path.join(self.pres_storage, "deposit_one")
        self.assertTrue(os.path.exists(full_object_path))

        inventory_path = os.path.join(full_object_path, "inventory.json")
        inventory_data = OcflRepositoryGatewayTest.read_inventory(inventory_path)
        self.assertEqual("deposit_one", inventory_data["id"])
        head_version = inventory_data["versions"][inventory_data["head"]]
        logical_paths = [path for paths in head_version["state"].values() for path in paths]
        self.assertSetEqual(
            set(["A.txt", "B/B.txt", "C/D/D.txt"]), set(logical_paths)
        )

        self.assertEqual("Adding first version!", head_version["message"])
        self.assertEqual("test", head_version["user"]["name"])
        self.assertEqual("mailto:test@example.edu", head_version["user"]["address"])

    def test_gateway_raises_when_committing_an_object_that_is_not_staged(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()

        with self.assertRaises(ObjectNotStagedException):
            gateway.commit_object_changes(
                "deposit_zero",
                Coordinator("test", "test@example.edu"),
                "Did I stage an object first?"
            )

    def test_gateway_commits_empty_object(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        gateway.commit_object_changes(
            "deposit_one", Coordinator("test", "test@example.edu"), "Adding empty version!"
        )

        object_files = gateway.get_object_files("deposit_one")
        self.assertListEqual([], object_files)

    def test_gateway_purges_object(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        package = self.deposit_dir.get_package("deposit_one")
        gateway.stage_object_files("deposit_one", package)
        gateway.commit_object_changes(
            "deposit_one", Coordinator("test", "test@example.edu"), "Adding first version!"
        )

        # Check for object in storage root
        full_object_path = os.path.join(self.pres_storage, "deposit_one")
        self.assertTrue(os.path.exists(full_object_path))

        gateway.purge_object("deposit_one")

        # Check that object is gone
        self.assertFalse(os.path.exists(full_object_path))

    # TO DO: Do we want to enforce this ourselves?
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
        package = self.deposit_dir.get_package("deposit_one")
        gateway.stage_object_files("deposit_one", package)
        gateway.commit_object_changes(
            "deposit_one", Coordinator("test", "test@example.edu"), "Adding first version!"
        )
        result = gateway.has_object("deposit_one")

        self.assertEqual(True, result)

    def test_gateway_provides_file_paths(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        package = self.deposit_dir.get_package("deposit_one")
        gateway.stage_object_files("deposit_one", package)
        gateway.commit_object_changes(
            "deposit_one", Coordinator("test", "test@example.edu"), "Adding first version!"
        )
        file_paths = gateway.get_file_paths("deposit_one")
        self.assertListEqual(["A.txt", "B/B.txt", "C/D/D.txt"], file_paths)

    def test_gateway_provides_object_files(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        package = self.deposit_dir.get_package("deposit_one")
        gateway.stage_object_files("deposit_one", package)
        gateway.commit_object_changes(
            "deposit_one", Coordinator("test", "test@example.edu"), "Adding first version!"
        )

        update_package = self.deposit_dir.get_package("deposit_one_update")
        gateway.stage_object_files("deposit_one", update_package)
        gateway.commit_object_changes(
            "deposit_one", Coordinator("test", "test@example.edu"), "Adding second version!"
        )

        object_files = gateway.get_object_files("deposit_one")
        prefix = os.path.join(self.pres_storage, "deposit_one")
        self.assertListEqual(
            [
                ObjectFile("A.txt", os.path.join(prefix, "v1", "content", "A.txt")),
                ObjectFile("B/B.txt", os.path.join(prefix, "v2", "content", "B", "B.txt")),
                ObjectFile("C/D/D.txt", os.path.join(prefix, "v1", "content", "C", "D", "D.txt")),
                ObjectFile("E.txt", os.path.join(prefix, "v2", "content", "E.txt"))
            ],
            object_files
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
        package = self.deposit_dir.get_package("deposit_one")
        gateway.stage_object_files("deposit_one", package)

        object_files = gateway.get_object_files("deposit_one", True)

        object_path = OcflRepositoryGatewayTest.get_hashed_n_tuple_object_path("deposit_one")
        prefix = os.path.join(self.extensions_path, object_path)

        self.assertListEqual(
            [
                ObjectFile("A.txt", os.path.join(prefix, "v1", "content", "A.txt")),
                ObjectFile("B/B.txt", os.path.join(prefix, "v1", "content", "B", "B.txt")),
                ObjectFile("C/D/D.txt", os.path.join(prefix, "v1", "content", "C", "D", "D.txt")),
            ],
            object_files
        )

    def test_gateway_provides_object_files_when_no_staged_ones_exist(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        package = self.deposit_dir.get_package("deposit_one")
        gateway.stage_object_files("deposit_one", package)
        gateway.commit_object_changes(
            "deposit_one", Coordinator("test", "test@example.edu"), "Adding first version!"
        )

        object_files = gateway.get_object_files("deposit_one", True)

        prefix = os.path.join(self.pres_storage, "deposit_one")
        self.assertListEqual(
            [
                ObjectFile("A.txt", os.path.join(prefix, "v1", "content", "A.txt")),
                ObjectFile("B/B.txt", os.path.join(prefix, "v1", "content", "B", "B.txt")),
                ObjectFile("C/D/D.txt", os.path.join(prefix, "v1", "content", "C", "D", "D.txt")),
            ],
            object_files
        )

    def test_gateway_provides_object_files_when_versioned_and_staged_files_exist(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_staged_object("deposit_one")
        package = self.deposit_dir.get_package("deposit_one")
        gateway.stage_object_files("deposit_one", package)
        gateway.commit_object_changes(
            "deposit_one", Coordinator("test", "test@example.edu"), "Adding first version!"
        )

        update_package = self.deposit_dir.get_package("deposit_one_update")
        gateway.stage_object_files("deposit_one", update_package)

        object_files = gateway.get_object_files("deposit_one", True)

        storage_prefix = os.path.join(self.pres_storage, "deposit_one")
        object_path_in_staging = OcflRepositoryGatewayTest.get_hashed_n_tuple_object_path("deposit_one")
        staging_prefix = os.path.join(self.extensions_path, object_path_in_staging)
        self.assertListEqual(
            [
                ObjectFile("A.txt", os.path.join(storage_prefix, "v1", "content", "A.txt")),
                ObjectFile("B/B.txt", os.path.join(staging_prefix, "v2", "content", "B", "B.txt")),
                ObjectFile("C/D/D.txt", os.path.join(storage_prefix, "v1", "content", "C", "D", "D.txt")),
                ObjectFile("E.txt", os.path.join(staging_prefix, "v2", "content", "E.txt"))
            ],
            object_files
        )

    def test_gateway_raises_when_providing_files_for_object_that_does_not_exist(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()

        with self.assertRaises(ObjectDoesNotExistException):
            gateway.get_object_files("deposit_zero")
