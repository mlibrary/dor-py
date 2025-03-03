import uuid
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Tuple

from dor.adapters.bag_adapter import BagAdapter
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
class DepositGroup:
    identifier: str
    date: datetime


@dataclass
class PackageResult:
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
        deposit_group: DepositGroup,
        output_path: Path,
        file_set_path: Path,
        timestamp: datetime
    ):
        self.file_provider = file_provider
        self.metadata = metadata
        self.deposit_group = deposit_group
        self.output_path = output_path
        self.file_set_path = file_set_path
        self.timestamp = timestamp

        self.root_resource_identifier: str = self.metadata["identifier"]
        self.package_identifier = self.root_resource_identifier + "_" + self.timestamp.strftime("%Y%m%d%H%M%S")
        self.package_path: Path = self.output_path / self.package_identifier

    def create_root_metadata_file(
        self,
        metadata_data: dict[str, Any],
        file_ending: str,
        serializer: Callable[[Any], str]
    ) -> FileMetadata:
        file_name = self.root_resource_identifier + file_ending
        locref = Path(self.root_resource_identifier) / "metadata" / file_name
        metadata_path = self.package_path / locref
        with open(metadata_path, "w") as descriptive_file:
            descriptive_file.write(serializer(metadata_data["data"]))
        return FileMetadata(
            id="_" + str(uuid.uuid4()),
            use=metadata_data["use"],
            ref=FileReference(
                locref=str(locref),
                mdtype=metadata_data.get("mdtype"),
                mimetype=metadata_data["mimetype"]
            )
        )

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
        descriptive_file_metadata = self.create_root_metadata_file(
            metadata_data=descriptive_data,
            file_ending=".metadata.json",
            serializer=lambda x: json.dumps(x, indent=4)
        )
        file_metadatas.append(descriptive_file_metadata)

        common_datas = [
            metadata_file_data for metadata_file_data in metadata_file_datas
            if metadata_file_data["use"] == "DESCRIPTIVE/COMMON"
        ]
        if len(common_datas) != 1:
            raise PackageMetadataError
        common_data = common_datas[0]
        common_file_metadata = self.create_root_metadata_file(
            metadata_data=common_data,
            file_ending=".common.json",
            serializer=lambda x: json.dumps(x, indent=4)
        )
        file_metadatas.append(common_file_metadata)

        provenance_datas = [
            metadata_file_data for metadata_file_data in metadata_file_datas
            if metadata_file_data["use"] == "PROVENANCE"
        ]
        if len(provenance_datas) != 1:
            raise PackageMetadataError
        provenance_data = provenance_datas[0]
        provenance_file_metadata = self.create_root_metadata_file(
            metadata_data=provenance_data,
            file_ending=".premis.object.xml",
            serializer=lambda x: x
        )
        file_metadatas.append(provenance_file_metadata)
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
                message=f"The following file sets were not found: {", ".join(missing_file_set_ids)}"
            )

        # Create root resource directory
        root_resource_path = self.package_path / self.root_resource_identifier
        self.file_provider.create_directory(root_resource_path)

        metadata_file_metadatas = self.create_root_metadata_files()

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
        dor_info = {
            "Action": "store",
            "Deposit-Group-Identifier": self.deposit_group.identifier,
            "Deposit-Group-Date": self.deposit_group.date,
            "Root-Identifier": self.root_resource_identifier,
            "Identifier": incorporated_file_set_ids,
        }
        bag = BagAdapter.make(self.package_path, self.file_provider)
        bag.add_dor_info(dor_info=dor_info)

        # Return success PackageResult
        return PackageResult(
            package_identifier=self.package_identifier,
            success=True,
            message="Generated package successfully!"
        )
