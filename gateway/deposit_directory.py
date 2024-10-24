import os

from gateway.package import Package

class DepositDirectory:
    path: str

    def __init__(self, path: str):
        self.path = path

    def resolve(self, sub_path: str) -> str:
        return os.path.join(self.path, sub_path)

    def get_package(self, package_path: str) -> Package:
        return Package(self, package_path)
