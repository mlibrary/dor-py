from pathlib import Path

from dor.providers.file_provider import FileProvider
from dor.providers.models import PackageResource, PreservationEvent
from dor.providers.parsers import DescriptorFileParser, PreservationEventFileParser


class DescriptorFileNotFound(Exception):
    pass


class ResourceProvider:

    def __init__(self, file_provider: FileProvider, resource_path: Path):
        self.file_provider: FileProvider = file_provider
        self.resource_path: Path = resource_path

    def get_descriptor_path(self) -> Path:
        file_paths = list((self.resource_path / "descriptor").iterdir())
        if len(file_paths) < 1:
            raise DescriptorFileNotFound()
        return file_paths[0]

    def get_resource(self) -> PackageResource:
        descriptor_file_parser = DescriptorFileParser(self.get_descriptor_path())

        event_file_paths = descriptor_file_parser.get_preservation_event_paths()
        pres_events: list[PreservationEvent] = []
        for event_file_path in event_file_paths:
            full_event_file_path = self.file_provider.get_replaced_path(
                self.resource_path, event_file_path
            )
            pres_events.append(PreservationEventFileParser(full_event_file_path).get_event())

        return PackageResource(
            id=descriptor_file_parser.get_id(),
            alternate_identifiers=descriptor_file_parser.get_alternate_identifiers(),
            type=descriptor_file_parser.get_type(),
            root=descriptor_file_parser.get_root(),
            events=pres_events,
            metadata_files=descriptor_file_parser.get_metadata_files(),
            data_files=descriptor_file_parser.get_data_files(),
            struct_maps=descriptor_file_parser.get_struct_maps(),
        )
