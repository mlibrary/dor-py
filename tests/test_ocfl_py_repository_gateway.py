import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any
from unittest import TestCase

from dor.providers.file_system_file_provider import FilesystemFileProvider
from gateway.coordinator import Coordinator
from gateway.exceptions import (
    ObjectAlreadyExistsError,
    ObjectDoesNotExistError
)
from gateway.object_file import ObjectFile
from gateway.ocfl_py_repository_gateway import OcflPyRepositoryGateway
from gateway.version_info import VersionInfo


class OcflPyRepositoryGatewayTest(TestCase):

    def setUp(self):
        test_deposit_path = Path("tests/fixtures/test_deposit")

        self.deposit_one_path = test_deposit_path / "deposit_one"
        self.deposit_one_update_path = test_deposit_path / "deposit_one_update"
        self.empty_deposit_path = test_deposit_path / "empty_deposit"

        self.storage_path = Path("tests/output/test_ocfl_py_repository_gateway")
        self.pres_storage = self.storage_path / "test_preservation_storage"

        self.file_provider = FilesystemFileProvider()
        if self.storage_path.exists():
            self.file_provider.delete_dir_and_contents(self.storage_path)
        self.file_provider.create_directories(self.storage_path)

        return super().setUp()

    @staticmethod
    def read_inventory(file_path: Path) -> dict[str, Any]:
        inventory_data = json.loads(file_path.read_text())
        return inventory_data

    def test_gateway_creates_repository(self):
        OcflPyRepositoryGateway(self.pres_storage).create_repository()

        namaste_path = self.pres_storage / "0=ocfl_1.1"
        self.assertTrue(namaste_path.exists())

    def test_gateway_creates_new_object(self):
        gateway = OcflPyRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_new_object(
            id="deposit_one",
            src_path=self.deposit_one_path,
            coordinator=Coordinator("test", "test@example.edu"),
            message="Adding first version!"
        )
 
        full_object_path = self.pres_storage / "deposit_one"
        self.assertTrue(full_object_path.exists())

        inventory_data = OcflPyRepositoryGatewayTest.read_inventory(
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

    def test_gateway_throws_error_when_creating_object_that_already_exists(self):
        gateway = OcflPyRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_new_object(
            id="deposit_one",
            src_path=self.deposit_one_path,
            coordinator=Coordinator("test", "test@example.edu"),
            message="Adding first version!"
        )
 
        with self.assertRaises(ObjectAlreadyExistsError):
            gateway.create_new_object(
                id="deposit_one",
                src_path=self.deposit_one_path,
                coordinator=Coordinator("test", "test@example.edu"),
                message="Adding first version again!"
            )

    def test_gateway_updates_existing_object(self):
        gateway = OcflPyRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_new_object(
            id="deposit_one",
            src_path=self.deposit_one_path,
            coordinator=Coordinator("test", "test@example.edu"),
            message="Adding first version!"
        )

        gateway.update_object(
            id="deposit_one",
            src_path=self.deposit_one_update_path,
            coordinator=Coordinator("test", "test@example.edu"),
            message="Adding second version!"
        )
 
        full_object_path = self.pres_storage / "deposit_one"
        self.assertTrue(full_object_path.exists())

        inventory_data = OcflPyRepositoryGatewayTest.read_inventory(
            full_object_path / "inventory.json"
        )
        self.assertEqual("deposit_one", inventory_data["id"])
        self.assertEqual(list(inventory_data["versions"].keys()), ["v1", "v2"])

        head_version = inventory_data["versions"][inventory_data["head"]]
        logical_paths = [
            path for paths in head_version["state"].values() for path in paths
        ]

        expected_logical_paths = set(["A.txt", "B/B.txt", "C/D/D.txt", "E.txt"])
        self.assertSetEqual(expected_logical_paths, set(logical_paths))

        self.assertEqual("Adding second version!", head_version["message"])
        self.assertEqual("test", head_version["user"]["name"])
        self.assertEqual("mailto:test@example.edu", head_version["user"]["address"])

    def test_gateway_throws_error_if_object_does_not_exist_on_update(self):
        gateway = OcflPyRepositoryGateway(self.pres_storage)
        gateway.create_repository()

        with self.assertRaises(ObjectDoesNotExistError):
            gateway.update_object(
                id="deposit_one",
                src_path=self.deposit_one_update_path,
                coordinator=Coordinator("test", "test@example.edu"),
                message="Adding second version!"
            )

    def test_gateway_indicates_it_does_not_have_an_object(self):
        gateway = OcflPyRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        result = gateway.has_object("deposit_zero")

        self.assertEqual(False, result)

    def test_gateway_indicates_it_does_have_an_object(self):
        gateway = OcflPyRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_new_object(
            id="deposit_one",
            src_path=self.deposit_one_path,
            coordinator=Coordinator("test", "test@example.edu"),
            message="Adding first version!"
        )
        result = gateway.has_object("deposit_one")

        self.assertEqual(True, result)

    def test_gateway_provides_object_files(self):
        gateway = OcflPyRepositoryGateway(self.pres_storage)
        gateway.create_repository()
        gateway.create_new_object(
            id="deposit_one",
            src_path=self.deposit_one_path,
            coordinator=Coordinator("test", "test@example.edu"),
            message="Adding first version!"
        )

        gateway.update_object(
            id="deposit_one",
            src_path=self.deposit_one_update_path,
            coordinator=Coordinator("test", "test@example.edu"),
            message="Adding second version!"
        )
 
        object_files = gateway.get_object_files("deposit_one")
        prefix = self.pres_storage / "deposit_one"
        self.assertSetEqual(
            set([
                ObjectFile(Path("A.txt"), prefix.joinpath("v1", "content", "A.txt")),
                ObjectFile(
                    Path("B/B.txt"), prefix.joinpath("v2", "content", "B", "B.txt")
                ),
                ObjectFile(
                    Path("C/D/D.txt"),
                    prefix.joinpath("v1", "content", "C", "D", "D.txt"),
                ),
                ObjectFile(Path("E.txt"), prefix.joinpath("v2", "content", "E.txt")),
            ]),
            set(object_files)
        )

    def test_gateway_raises_when_providing_files_for_object_that_does_not_exist(self):
        gateway = OcflPyRepositoryGateway(self.pres_storage)
        gateway.create_repository()

        with self.assertRaises(ObjectDoesNotExistError):
            gateway.get_object_files("deposit_zero")

    def test_gateway_logs_version_info_for_object(self):
        gateway = OcflPyRepositoryGateway(self.pres_storage)
        gateway.create_repository()

        timestamp = datetime.now(tz=UTC)

        gateway.create_new_object(
            id="deposit_one",
            src_path=self.deposit_one_path,
            coordinator=Coordinator("test", "test@example.edu"),
            message="Adding first version!",
            timestamp=timestamp
        )

        log = gateway.log("deposit_one")
        assert len(log) == 1
        expected_version_info = VersionInfo(
            version=1,
            author='test <mailto:test@example.edu>',
            date=timestamp,
            message='Adding first version!'
        )
        self.assertEqual(log[0], expected_version_info)

    def test_gateway_logs_by_default_in_descending_order(self):
        gateway = OcflPyRepositoryGateway(self.pres_storage)
        gateway.create_repository()

        first_timestamp = datetime.now(tz=UTC)
        gateway.create_new_object(
            id="deposit_one",
            src_path=self.deposit_one_path,
            coordinator=Coordinator("test", "test@example.edu"),
            message="Adding first version!",
            timestamp=first_timestamp
        )

        second_timestamp = datetime.now(tz=UTC)
        gateway.update_object(
            id="deposit_one",
            src_path=self.deposit_one_update_path,
            coordinator=Coordinator("test", "test@example.edu"),
            message="Adding second version!",
            timestamp=second_timestamp
        )

        log = gateway.log("deposit_one")
        self.assertEqual(log[0].version, 2)
        self.assertEqual(log[1].version, 1)

    def test_gateway_logs_optionally_in_ascending_order(self):
        gateway = OcflPyRepositoryGateway(self.pres_storage)
        gateway.create_repository()

        first_timestamp = datetime.now(tz=UTC)
        gateway.create_new_object(
            id="deposit_one",
            src_path=self.deposit_one_path,
            coordinator=Coordinator("test", "test@example.edu"),
            message="Adding first version!",
            timestamp=first_timestamp
        )

        second_timestamp = datetime.now(tz=UTC)
        gateway.update_object(
            id="deposit_one",
            src_path=self.deposit_one_update_path,
            coordinator=Coordinator("test", "test@example.edu"),
            message="Adding second version!",
            timestamp=second_timestamp
        )

        log = gateway.log("deposit_one", reversed=False)
        self.assertEqual(log[0].version, 1)
        self.assertEqual(log[1].version, 2)
