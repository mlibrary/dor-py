from pathlib import Path

from gateway.disk_package import DiskPackage

class DepositDirectory:
    path: Path

    def __init__(self, path: Path):
        self.path = path

    def resolve(self, sub_path: Path) -> Path:
        return self.path / sub_path

    def get_package(self, package_path: Path) -> DiskPackage:
        return DiskPackage(self, package_path)
