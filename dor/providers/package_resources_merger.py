from dor.providers.models import PackageResource, StructMapType


class PackageResourcesMerger:
    def __init__(self, incoming: list[PackageResource], current: list[PackageResource]):
        self.incoming = incoming
        self.current = current

    def merge_changes(self):
        resources = []

        incoming_map = self._index(self.incoming)
        current_map = self._index(self.current)

        for package_resource in self.current:
            if package_resource.id in incoming_map:
                resources.append(
                    self._merge_resource(package_resource, incoming_map[package_resource.id])
                )
            else:
                resources.append(package_resource)

        for resource in self.incoming:
            if not resource.id in current_map:
                resources.append(resource)

        return resources

    def _index(self, resources, attr='id'):
        index = {}
        for resource in resources:
            index[getattr(resource, attr)] = resource
        return index

    def _merge_resource(self, current_resource: PackageResource, incoming_resource: PackageResource) -> PackageResource:
        merged_events = []
        merged_metadata_files = []
        merged_data_files = []
        merged_struct_maps = []

        merged_events = self._merge_lists(
            current_resource.events,
            incoming_resource.events,
        )

        merged_metadata_files = self._merge_file_lists(
            current_resource.metadata_files,
            incoming_resource.metadata_files,
        )

        merged_data_files = self._merge_file_lists(
            current_resource.data_files,
            incoming_resource.data_files,
        )

        if incoming_resource.struct_maps and incoming_resource.struct_maps[0].type == StructMapType.physical:
            merged_struct_maps = self._merge_lists(
                current_resource.struct_maps,
                incoming_resource.struct_maps,
                "id",
            )
        else:
            merged_struct_maps = current_resource.struct_maps

        return PackageResource(
            id=incoming_resource.id,
            type=incoming_resource.type,
            alternate_identifiers=incoming_resource.alternate_identifiers,
            events=merged_events,
            metadata_files=merged_metadata_files,
            data_files=merged_data_files,
            struct_maps=merged_struct_maps
        )

    def _merge_lists(self, a, b, attr='identifier'):
        merged = []
        index = self._index(b, attr)
        for value in a + b:
            key = getattr(value, attr)
            if value in merged:
                continue
            elif key in index:
                merged.append(index[key])
            elif not value in merged:
                merged.append(value)
        return merged

    def _merge_file_lists(self, a, b):
        merged = []
        index = {}
        for value in b:
            index[value.ref.locref] = value

        for value in a + b:
            key = value.ref.locref
            if value in merged:
                continue
            elif key in index:
                merged.append(index[key])
            elif not value in merged:
                merged.append(value)
        return merged
