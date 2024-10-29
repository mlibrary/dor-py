import os
from unittest import TestCase

from gateway.deposit_directory import DepositDirectory
from gateway.exceptions import NoContentError
from gateway.package import Package

class PackageTest(TestCase):

    def setUp(self):
        self.test_deposit_path: str = os.path.join("tests", "fixtures", "test_deposit")
        self.deposit_dir = DepositDirectory(self.test_deposit_path)

        self.deposit_one_path: str = os.path.join(self.test_deposit_path, "deposit_one")
        self.empty_deposit_path: str = os.path.join(self.test_deposit_path, "empty_deposit")

        if not os.path.exists(self.empty_deposit_path):
            os.mkdir(self.empty_deposit_path)

        return super().setUp()
    
    def test_package_provides_root_path(self):
        package = Package(self.deposit_dir, "deposit_one")
        self.assertEqual(
            os.path.join(self.test_deposit_path, "deposit_one"),
            package.get_root_path()
        )

    def test_nonexistent_package_fails_validation(self):
        with self.assertRaises(NoContentError):
            Package(self.deposit_dir, "no_such_deposit")

    def test_existing_package_passes_validation(self):
        Package(self.deposit_dir, "deposit_one")

    def test_empty_package_contains_no_files(self):
        package = Package(self.deposit_dir, "empty_deposit")
        self.assertTrue(len(package.get_file_paths()) == 0)

    def test_mixed_package_contains_expected_files(self):
        package = Package(self.deposit_dir, "deposit_one")
        self.assertSetEqual(
            set(["A.txt", "B/B.txt", "C/D/D.txt"]),
            set(package.get_file_paths())
        )
