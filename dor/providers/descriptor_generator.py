from pathlib import Path
from datetime import datetime, UTC

from dor.settings import template_env
from dor.providers.models import PackageResource

def relative_path_or_not(locref: str):
    if locref.startswith("https://"):
        return locref
    return f"../{locref}"

def build_descriptor_filename(resource):
    return f"{resource.id}.{resource.type.lower().replace(" ", "_")}.mets2.xml"

class DescriptorGenerator:
    def __init__(self, package_path: Path, resources: list[PackageResource]):
        self.package_path = package_path
        self.resources = resources
        self.entries = []

    def write_files(self):
        struct_map_locref_data = {}
        for resource in self.resources:
            if resource.type == "Asset":
                identifier = f"urn:dor:{resource.id}"
                struct_map_locref_data[identifier] = build_descriptor_filename(resource)

        entity_template = template_env.get_template("preservation_mets.xml")
        for resource in self.resources:
            xmldata = entity_template.render(
                relative_path_or_not=relative_path_or_not,
                resource=resource,
                struct_map_locref_data=struct_map_locref_data,
                action="stored",
                create_date=datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            filename = Path(f"{resource.id}/descriptor/{build_descriptor_filename(resource)}")
            output_filename = self.package_path / filename
            output_filename.parent.mkdir(parents=True)
            with (output_filename).open("w") as f:
                f.write(xmldata)
            self.entries.append(filename)
