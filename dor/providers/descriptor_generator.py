from pathlib import Path
from datetime import datetime, UTC

from dor.providers.models import PackageResource
from dor.settings import template_env


def build_descriptor_file_path(resource):
    return Path(str(resource.id)) / "descriptor" / f"{resource.id}.{resource.type.lower().replace(" ", "_")}.mets2.xml"

class DescriptorGenerator:
    def __init__(self, package_path: Path, resources: list[PackageResource]):
        self.package_path = package_path
        self.resources = resources

        self.entries = []

    def write_files(self):
        struct_map_locref_data = {}
        for resource in self.resources:
            if resource.type == "File Set":
                identifier = str(resource.id)
                struct_map_locref_data[identifier] = build_descriptor_file_path(resource)

        entity_template = template_env.get_template("preservation_mets.xml")
        for resource in self.resources:
            xmldata = entity_template.render(
                resource=resource,
                struct_map_locref_data=struct_map_locref_data,
                create_date=datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            descriptor_file_path = build_descriptor_file_path(resource)
            output_path = self.package_path / descriptor_file_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with (output_path).open("w") as f:
                f.write(xmldata)
            self.entries.append(descriptor_file_path)
