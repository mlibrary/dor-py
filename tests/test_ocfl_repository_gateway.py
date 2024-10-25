import hashlib
import json
import os
import shutil
from typing import Any
from unittest import TestCase

from gateway.coordinator import Coordinator
from gateway.deposit_directory import DepositDirectory
from gateway.ocfl_repository_gateway import OcflRepositoryGateway

class OcflRepositoryGatewayTest(TestCase):

    def setUp(self):
        test_deposit_path = os.path.join("tests", "fixtures", "test_deposit")
        self.deposit_dir = DepositDirectory(test_deposit_path)
        
        self.storage_path = os.path.join("tests", "test_storage")
        self.pres_storage = os.path.join(self.storage_path, "test_preservation_storage")
        
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

    def test_gateway_creates_empty_object(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_empty_object("deposit_one")

        # TO DO: What do I test here? Doesn't seem to be any filesystem side effects...

    def test_gateway_stages_changes(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_empty_object("deposit_one")
        package = self.deposit_dir.get_package("deposit_one")
        gateway.stage_object_files("deposit_one", package)

        # Check for changes under extensions
        extensions_path = os.path.join(self.pres_storage, "extensions", "rocfl-staging")
        self.assertTrue(os.path.exists(extensions_path))

        object_path = OcflRepositoryGatewayTest.get_hashed_n_tuple_object_path("deposit_one")
        full_object_path = os.path.join(extensions_path, object_path)
        self.assertTrue(os.path.exists(full_object_path))

        inventory_path = os.path.join(full_object_path, "inventory.json")
        inventory_data = OcflRepositoryGatewayTest.read_inventory(inventory_path)
        self.assertEqual("deposit_one", inventory_data["id"])
        head_version = inventory_data["versions"][inventory_data["head"]]
        logical_paths = [path for paths in head_version["state"].values() for path in paths]
        self.assertSetEqual(
            set(["A.txt", "B/B.txt", "C/D/D.txt"]), set(logical_paths)
        )

    def test_gateway_commits_changes(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_empty_object("deposit_one")
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

    def test_gateway_provides_file_paths(self):
        gateway = OcflRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_empty_object("deposit_one")
        package = self.deposit_dir.get_package("deposit_one")
        gateway.stage_object_files("deposit_one", package)
        gateway.commit_object_changes(
            "deposit_one", Coordinator("test", "test@example.edu"), "Adding first version!"
        )
        file_paths = gateway.get_file_paths("deposit_one")
        self.assertListEqual(["A.txt", "B/B.txt", "C/D/D.txt"], file_paths)
