import os
from pathlib import Path
from unittest import TestCase

from gateway.deposit_directory import DepositDirectory
from gateway.exceptions import NoContentError
from gateway.package import Package

class PackageTest(TestCase):

    def setUp(self):
        self.test_deposit_path: Path = Path("tests/fixtures/test_deposit")
        self.deposit_dir = DepositDirectory(self.test_deposit_path)

        self.deposit_one_path: Path = self.test_deposit_path / "deposit_one"
        self.empty_deposit_path: Path = self.test_deposit_path / "empty_deposit"

        if not self.empty_deposit_path.exists():
            os.mkdir(self.empty_deposit_path)

        return super().setUp()
    
    def test_package_provides_root_path(self):
        package = Package(self.deposit_dir, Path("deposit_one"))
        self.assertEqual(
            self.test_deposit_path / "deposit_one",
            package.get_root_path()
        )

    def test_nonexistent_package_fails_validation(self):
        with self.assertRaises(NoContentError):
            Package(self.deposit_dir, Path("no_such_deposit"))

    def test_existing_package_passes_validation(self):
        Package(self.deposit_dir, Path("deposit_one"))

    def test_empty_package_contains_no_files(self):
        package = Package(self.deposit_dir, Path("empty_deposit"))
        self.assertTrue(len(package.get_file_paths()) == 0)

    def test_mixed_package_contains_expected_files(self):
        package = Package(self.deposit_dir, Path("deposit_one"))
        self.assertSetEqual(
            set([Path("A.txt"), Path("B/B.txt"), Path("C/D/D.txt")]),
            set(package.get_file_paths())
        )
