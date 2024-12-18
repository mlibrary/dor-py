from pathlib import Path
from typing import Dict

from dor.providers.models import PackageResource
from dor.providers.parsers import DescriptorFileParser
from utils.element_adapter import ElementAdapter


class PackageResourceProvider:

    namespaces: dict[str, str] = {
        "METS": "http://www.loc.gov/METS/v2",
        "PREMIS": "http://www.loc.gov/premis/v3",
    }
    
    def __init__(self, descriptor_path: Path):
        self.descriptor_path = descriptor_path
        self._descriptor_files: Dict[Path, ElementAdapter] = {}
        self._read_descriptor_files()

    def _read_descriptor_files(self):
        for file in self.descriptor_path.iterdir():
            descriptor_text = file.read_text()
            self._descriptor_files[file] = ElementAdapter.from_string(descriptor_text, self.namespaces)

    @property
    def descriptor_files(self):
        return self._descriptor_files 
    
    def get_resources(self) -> list[PackageResource]:
        package_resources: list[PackageResource] = []
        for file_element in self._descriptor_files.values():
            resource = DescriptorFileParser(file_element, self.descriptor_path).get_resource()
            package_resources.append(resource)
            
        return package_resources
        