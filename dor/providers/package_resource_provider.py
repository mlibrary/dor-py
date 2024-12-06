from pathlib import Path

from .parsers import DescriptorFileParser


class PackageResourceProvider:

    def __init__(self, data_path: Path):
        self.data_path = data_path

    @property
    def descriptor_files(self):
        descriptor_path = self.data_path / "descriptor"
        return [file for file in descriptor_path.iterdir()]

    def get_resources(self):
        return [
            DescriptorFileParser(file).get_resource() for file in self.descriptor_files
        ]
