from pathlib import Path

from dor.providers.file_provider import FileProvider

from .parsers import DescriptorFileParser

class PackageResourceProvider:

    def __init__(self, data_path: Path, file_provider: FileProvider):
        self.data_path = data_path
        self.file_provider = file_provider

    @property
    def descriptor_files(self):
        descriptor_files = []
        for object_path in self.data_path.iterdir():
            descriptor_path = object_path / "descriptor"
            descriptor_files.extend(descriptor_path.iterdir())
        return descriptor_files

    def get_resources(self):
        return [
            DescriptorFileParser(file, self.file_provider).get_resource() for file in self.descriptor_files
        ]
