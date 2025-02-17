from pathlib import Path

from dor.providers.file_provider import FileProvider
from dor.providers.resource_provider import ResourceProvider

class PackageResourceProvider:

    def __init__(self, data_path: Path, file_provider: FileProvider):
        self.data_path = data_path
        self.file_provider = file_provider

    def get_resources(self):
        return [
            ResourceProvider(self.file_provider, resource_path).get_resource()
            for resource_path in self.data_path.iterdir()
        ]
