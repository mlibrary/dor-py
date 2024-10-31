from pathlib import Path
from unittest import TestCase

from gateway.deposit_directory import DepositDirectory

class DepositDirectoryTest(TestCase):

    def setUp(self):
        self.test_deposit_path = Path("tests/fixtures/test_deposit")
        self.deposit_dir = DepositDirectory(self.test_deposit_path)

        return super().setUp()
    
    def test_deposit_directory_expands_package_paths_to_full_ones(self):
        package_path: Path = Path("some_package")
        self.assertEqual(
            self.test_deposit_path / package_path,
            self.deposit_dir.resolve(package_path)
        )

    def test_deposit_directory_provides_access_to_packages(self):
        self.deposit_dir.get_package(Path("deposit_one"))
