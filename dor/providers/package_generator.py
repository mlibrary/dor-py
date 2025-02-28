import uuid
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Tuple

from dor.providers.file_provider import FileProvider
from dor.providers.models import (
    AlternateIdentifier,
    FileMetadata,
    FileReference,
    PackageResource,
    StructMap,
    StructMapItem,
    StructMapType
)
from dor.settings import template_env


@dataclass
class PackageResult():
    package_identifier: str
    success: bool
    message: str


class PackageMetadataError(Exception):
    pass


class PackageGenerator:

    def __init__(
        self,
        file_provider: FileProvider,
        metadata: dict[str, Any],
        output_path: Path,
        file_set_path: Path,
        timestamp: datetime
    ):
        self.file_provider = file_provider
        self.metadata = metadata
        self.output_path = output_path
        self.file_set_path = file_set_path
        self.timestamp = timestamp

        self.root_resource_identifier: str = self.metadata["identifier"]
        self.package_identifier = self.root_resource_identifier + "_" + self.timestamp.strftime("%Y%m%d%H%M%S")
        self.package_path: Path = self.output_path / self.package_identifier

    def create_root_metadata_files(self) -> list[FileMetadata]:
        """Create metadata files (descriptive, common, PREMIS)"""

        file_metadatas: list[FileMetadata] = []
        self.file_provider.create_directory(
            self.package_path / self.root_resource_identifier / "metadata"
        )

        metadata_file_datas = self.metadata["md"]
        descriptive_datas = [
            metadata_file_data for metadata_file_data in metadata_file_datas
            if metadata_file_data["use"] == "DESCRIPTIVE"
        ]
        if len(descriptive_datas) != 1:
            raise PackageMetadataError
        descriptive_data = descriptive_datas[0]
        descriptive_file_name = self.root_resource_identifier + ".metadata.json"
        descriptive_locref = Path(self.root_resource_identifier) / "metadata" / descriptive_file_name
        descriptive_metadata_path = self.package_path / descriptive_locref
        with open(descriptive_metadata_path, "w") as descriptive_file:
            descriptive_file.write(json.dumps(descriptive_data["data"], indent=4))
        file_metadatas.append(FileMetadata(
            id="_" + str(uuid.uuid4()),
            use=descriptive_data["use"],
            ref=FileReference(
                locref=str(descriptive_locref),
                mdtype=descriptive_data.get("mdtype"),
                mimetype="application/json"
            )
        ))

        common_datas = [
            metadata_file_data for metadata_file_data in metadata_file_datas
            if metadata_file_data["use"] == "DESCRIPTIVE/COMMON"
        ]
        if len(common_datas) != 1:
            raise PackageMetadataError
        common_data = common_datas[0]
        common_file_name = self.root_resource_identifier + ".common.json"
        common_locref = Path(self.root_resource_identifier) / "metadata" / common_file_name
        common_metadata_path = self.package_path / common_locref
        with open(common_metadata_path, "w") as common_file:
            common_file.write(json.dumps(common_data["data"], indent=4))
        file_metadatas.append(FileMetadata(
            id="_" + str(uuid.uuid4()),
            use=common_data["use"],
            ref=FileReference(
                locref=str(common_locref),
                mdtype=common_data.get("mdtype"),
                mimetype="application/json"
            )
        ))

        provenance_datas = [
            metadata_file_data for metadata_file_data in metadata_file_datas
            if metadata_file_data["use"] == "PROVENANCE"
        ]
        if len(provenance_datas) != 1:
            raise PackageMetadataError
        provenance_data = provenance_datas[0]
        provenance_file_name = self.root_resource_identifier + ".premis.object.xml"
        provenance_locref = Path(self.root_resource_identifier) / "metadata" / provenance_file_name
        provenance_metadata_path = self.package_path / provenance_locref
        with open(provenance_metadata_path, "w") as provenance_file:
            provenance_file.write(provenance_data["data"])
        file_metadatas.append(FileMetadata(
            id="_" + str(uuid.uuid4()),
            use=str(provenance_data["use"]),
            ref=FileReference(
                locref=str(provenance_locref),
                mdtype=provenance_data.get("mdtype"),
                mimetype="text/xml"
            )
        ))
        return file_metadatas

    def get_struct_maps(self) -> list[StructMap]:
        struct_maps = []
        for structure in self.metadata["structure"]:
            items = [
                StructMapItem(
                    order=item["order"],
                    label=item["orderlabel"],
                    file_set_id="urn:dor:" + item["locref"],
                    type=item.get("type")
                )
                for item in structure["items"]
            ]
            struct_maps.append(
                StructMap(
                    id=str(uuid.uuid4()),
                    type=StructMapType[structure["type"].upper()],
                    items=items
                )
            )
        return struct_maps

    def incorporate_file_sets(self, physical_struct_map: StructMap) -> Tuple[list[str], list[str]]:
        file_set_directories = [
            entry.name
            for entry in self.file_set_path.iterdir()
            if entry.is_dir()
        ]
        incorporated_file_set_ids = []
        missing_file_set_ids = []
        for struct_map_item in physical_struct_map.items:
            file_set_id = struct_map_item.file_set_id.replace("urn:dor:", "")
            if file_set_id in file_set_directories:
                self.file_provider.clone_directory_structure(
                    self.file_set_path / file_set_id,
                    self.package_path / file_set_id
                )
                incorporated_file_set_ids.append(file_set_id)
            else:
                missing_file_set_ids.append(file_set_id)
        return incorporated_file_set_ids, missing_file_set_ids

    def create_root_descriptor_file(
        self,
        resource: PackageResource,
        file_set_ids: list[str]
    ) -> None:
        descriptor_path = self.package_path / self.root_resource_identifier / "descriptor"
        self.file_provider.create_directory(descriptor_path)
        descriptor_file_name = f"{self.root_resource_identifier}.monograph.mets2.xml"

        struct_map_locref_data = {}
        for file_set_id in file_set_ids:
            identifier = "urn:dor:" + file_set_id
            struct_map_locref_data[identifier] = Path(file_set_id) / "descriptor" / f"{file_set_id}.file_set.mets2.xml"

        entity_template = template_env.get_template("preservation_mets.xml")
        xmldata = entity_template.render(
            resource=resource,
            struct_map_locref_data=struct_map_locref_data,
            create_date=self.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        with (descriptor_path / descriptor_file_name).open("w") as file:
            file.write(xmldata)

    def generate(self) -> PackageResult:        
        # print(json.dumps(metadata, indent=4))
        # Validate metadata?
        # Designate some directory for package payload
        self.file_provider.create_directory(self.package_path)

        # Create root resource directory
        root_resource_path = self.package_path / self.root_resource_identifier
        self.file_provider.create_directory(root_resource_path)

        metadata_file_metadatas = self.create_root_metadata_files()

        # Pull in file set resources
        struct_maps = self.get_struct_maps()
        physical_struct_maps = [
            struct_map for struct_map in struct_maps
            if struct_map.type == StructMapType.PHYSICAL
        ]
        if len(physical_struct_maps) != 1:
            raise PackageMetadataError
        physical_struct_map = physical_struct_maps[0]
        incorporated_file_set_ids, missing_file_set_ids = self.incorporate_file_sets(physical_struct_map)
        if len(missing_file_set_ids) > 0:
            return PackageResult(
                package_identifier=self.package_identifier,
                success=False,
                message="The following file sets were not found: {missing_file_set_ids}"
            )

        # Create descriptor METS (DescriptorGenerator?)
        resource = PackageResource(
            id=uuid.UUID(self.root_resource_identifier),
            type="Monograph",
            root=True,
            alternate_identifier=AlternateIdentifier(id="something", type="DLXS"),
            events=[],
            metadata_files=metadata_file_metadatas,
            data_files=[],
            struct_maps=struct_maps
        )
        self.create_root_descriptor_file(resource, incorporated_file_set_ids)

        # Create bag in inbox based on payload directory (BagAdapter?)
            # Generate dor-info.txt
        # Return success PackageResult
        return PackageResult(
            package_identifier=self.package_identifier,
            success=True,
            message="Generated package successfully!"
        )
