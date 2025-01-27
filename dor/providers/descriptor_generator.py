from pathlib import Path
from datetime import datetime, UTC

from dor.settings import S, template_env
from dor.domain.models import Bin

class DescriptorGenerator:
    def __init__(self, output_path: Path, bin: Bin):
        self.output_path = output_path
        self.bin = bin

    def write_files(self):
        struct_map_locref_data = {}
        for resource in self.bin.package_resources:
            if resource.type == "Asset":
                identifier = f"urn:dor:{resource.id}"
                struct_map_locref_data[identifier] = f"{resource.id}.{resource.type.lower()}.mets2.xml"

        entity_template = template_env.get_template("preservation_mets.xml")
        for resource in self.bin.package_resources:
            xmldata = entity_template.render(
                resource=resource,
                struct_map_locref_data=struct_map_locref_data,
                action="stored",
                create_date=datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            filename = self.output_path / f"{resource.id}.{resource.type.lower()}.mets2.xml"
            with filename.open("w") as f:
                f.write(xmldata)
