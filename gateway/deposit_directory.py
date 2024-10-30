from pathlib import Path

from gateway.package import Package

class DepositDirectory:
    path: Path

    def __init__(self, path: Path):
        self.path = path

    def resolve(self, sub_path: Path) -> Path:
        return self.path / sub_path

    def get_package(self, package_path: Path) -> Package:
        return Package(self, package_path)
