from pathlib import Path

from dor.providers.FileProvider import FileProvider

from .parsers import DescriptorFileParser

class PackageResourceProvider:

    def __init__(self, data_path: Path, file_provider: FileProvider):
        self.data_path = data_path
        self.file_provider = file_provider

    @property
    def descriptor_files(self):
        descriptor_path = self.data_path / "descriptor"
        return [file for file in descriptor_path.iterdir()]

    def get_resources(self):
        return [
            DescriptorFileParser(file, self.file_provider).get_resource() for file in self.descriptor_files
        ]
        