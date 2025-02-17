from pathlib import Path

from dor.providers.file_provider import FileProvider
from dor.providers.models import PackageResource
from dor.providers.parsers import DescriptorFileParser, PreservationEventFileParser


class DescriptorFileNotFound(Exception):
    pass


class ResourceProvider:

    def __init__(self, file_provider: FileProvider, resource_path: Path):
        self.file_provider: FileProvider = file_provider
        self.resource_path: Path = resource_path 

    def get_descriptor_path(self) -> Path:
        file_paths = list((self.resource_path / "descriptor").iterdir())
        if len(file_paths) < 0:
            raise DescriptorFileNotFound()
        return file_paths[0]

    def get_resource(self) -> PackageResource:
        descriptor_file_parser = DescriptorFileParser(
            self.get_descriptor_path(),
            self.file_provider
        )

        pres_file_paths = descriptor_file_parser.get_preservation_file_paths()
        event_file_paths = [
            pres_file_path for pres_file_path in pres_file_paths
            if "event" in pres_file_path
        ]
        pres_events = []
        for event_file_path in event_file_paths:
            full_event_file_path = self.file_provider.get_replaced_path(
                self.resource_path, event_file_path
            )
            event = PreservationEventFileParser(full_event_file_path).get_event()
            pres_events.append(event)

        return PackageResource(
            id=descriptor_file_parser.get_id(),
            alternate_identifier=descriptor_file_parser.get_alternate_identifier(),
            type=descriptor_file_parser.get_type(),
            events=pres_events,
            metadata_files=descriptor_file_parser.get_metadata_files(),
            data_files=descriptor_file_parser.get_data_files(),
            struct_maps=descriptor_file_parser.get_struct_maps(),
        )
