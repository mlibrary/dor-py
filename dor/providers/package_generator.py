import json
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Callable

from dor.adapters.bag_adapter import BagAdapter
from dor.providers.file_provider import FileProvider
from dor.providers.models import (
    Agent,
    AlternateIdentifier,
    DepositGroup,
    FileMetadata,
    FileReference,
    PackageResource,
    PreservationEvent,
    StructMap,
    StructMapItem,
    StructMapType
)
from dor.providers.repository_client import RepositoryClient
from dor.providers.serializers import PreservationEventSerializer
from dor.settings import template_env
from utils.minter import minter


@dataclass
class PackageResult:
    package_identifier: str
    deposit_group_identifier: str
    success: bool
    message: str


class PackageMetadataError(Exception):

    def __init__(self, message: str):
        super().__init__(message)

        self.message = message


def serialize_provenance(data: Any) -> str:
    template = template_env.get_template("premis_object.xml")
    xmldata = template.render(
        alternate_identifier=data["alternate_identifier"],
        scans_count=data["scans_count"],
        collid=data["collid"]
    )
    return xmldata


class FileSetsPendingError(Exception):

    def __init__(self, message: str):
        super().__init__(message)

        self.message = message


class FileSetsPending:

    @classmethod
    def sort_job_index_key(cls, path: Path):
        return int(os.path.basename(path))

    def __init__(self, file_provider: FileProvider, root_path: Path):
        self.file_provider = file_provider
        self.root_path = root_path

    def pending(self, file_set_id: str) -> bool:
        return (self.root_path / file_set_id).exists()

    def push(self, file_set_id: str, destination_path: Path) -> None:
        if not self.pending(file_set_id):
            raise FileSetsPendingError(
                f"Expected file set \"{file_set_id}\" to be pending"
            )

        file_set_directories = [
            entry.name for entry in sorted((self.root_path / file_set_id).iterdir(), key=self.sort_job_index_key, reverse=True)
            if entry.is_dir()
        ]

        self.file_provider.clone_directory_structure(
            self.root_path / file_set_id / file_set_directories[0] / "build" / file_set_id,
            destination_path / file_set_id
        )


class PackageGenerator:

    def __init__(
        self,
        file_provider: FileProvider,
        repository_client: RepositoryClient,
        metadata: dict[str, Any],
        deposit_group: DepositGroup,
        output_path: Path,
        file_sets_path: Path,
        timestamp: datetime,
        collection_manager_email: str = "example@org.edu",
    ):
        self.file_provider = file_provider
        self.metadata = metadata
        self.deposit_group = deposit_group
        self.output_path = output_path
        self.file_sets_path = file_sets_path
        self.file_sets_pending = FileSetsPending(self.file_provider, self.file_sets_path)
        self.timestamp = timestamp
        self.repository_client = repository_client
        self.collection_manager_email = collection_manager_email

        self.root_resource_identifier: str = self.metadata["identifier"]
        self.type: str = self.metadata["type"]
        self.package_identifier = self.root_resource_identifier + "_" + self.timestamp.strftime("%Y%m%d%H%M%S")
        self.package_path: Path = self.output_path / self.package_identifier

    def clear_package_path(self):
        self.file_provider.delete_dir_and_contents(self.package_path)

    def get_package_result(self, success: bool, message: str) -> PackageResult:
        return PackageResult(
            package_identifier=self.package_identifier,
            deposit_group_identifier=self.deposit_group.identifier,
            success=success,
            message=message
        )

    def get_metadata_file_data(self, use: str) -> dict[str, Any]:
        matching_file_datas = [
            metadata_file_data for metadata_file_data in self.metadata["md"]
            if metadata_file_data["use"] == use
        ]
        if len(matching_file_datas) != 1:
            raise PackageMetadataError(
                f"Expected to find a single instance of metadata file data for use \"{use}\" " +
                f"but found {len(matching_file_datas)}"
            )
        return matching_file_datas[0]

    def get_metadata_file_path(self, file_ending: str) -> Path:
        file_name = self.root_resource_identifier + file_ending
        locref = Path(self.root_resource_identifier) / "metadata" / file_name
        return locref

    @staticmethod
    def get_file_metadata(file_path: Path, metadata_data: dict[str, Any]) -> FileMetadata:
        return FileMetadata(
            id="_" + minter(),
            use=metadata_data["use"],
            ref=FileReference(
                locref=str(file_path),
                mdtype=metadata_data.get("mdtype"),
                mimetype=metadata_data["mimetype"]
            )
        )

    def create_ingest_event(self) -> PreservationEvent:
        event = PreservationEvent(
            identifier=minter(),
            type="ingest",
            datetime=datetime.now(tz=UTC),
            detail="No detail provided.",
            agent=Agent(address=self.collection_manager_email, role="packaging")
        )
        return event

    def create_ingest_event_file_metadata(self, file_path: Path) -> FileMetadata:
        return FileMetadata(
            id="_" + minter(),
            use="function:event",
            ref=FileReference(
                locref=str(file_path),
                mdtype="PREMIS",
                mimetype="text/xml+premis"
            )
        )

    def create_root_metadata_file(
        self,
        file_path: Path,
        data: Any,
        serializer: Callable[[Any], str]
    ) -> None:
        metadata_path = self.package_path / file_path
        with open(metadata_path, "w") as descriptive_file:
            descriptive_file.write(serializer(data))

    def get_struct_maps(self) -> list[StructMap]:
        struct_maps = []
        for structure in self.metadata["structure"]:
            items = [
                StructMapItem(
                    order=item["order"],
                    label=item["orderlabel"],
                    file_set_id=item["locref"],
                    type=item.get("type")
                )
                for item in structure["items"]
            ]
            struct_maps.append(
                StructMap(
                    id=str(uuid.uuid4()),
                    type=StructMapType(structure["type"]),
                    items=items
                )
            )
        return struct_maps

    def create_root_descriptor_file(
        self,
        resource: PackageResource,
        file_set_ids: list[str]
    ) -> None:
        """Create root resource's descriptor file using a template"""

        descriptor_path = self.package_path / self.root_resource_identifier / "descriptor"
        self.file_provider.create_directory(descriptor_path)
        descriptor_file_name = f"{self.root_resource_identifier}.monograph.mets2.xml"

        struct_map_locref_data = {}
        for file_set_id in file_set_ids:
            struct_map_locref_data[file_set_id] = Path(file_set_id) / "descriptor" / f"{file_set_id}.file_set.mets2.xml"

        entity_template = template_env.get_template("preservation_mets.xml")
        xmldata = entity_template.render(
            resource=resource,
            object_identifier=resource.id,
            struct_map_locref_data=struct_map_locref_data,
            create_date=self.timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        with (descriptor_path / descriptor_file_name).open("w") as file:
            file.write(xmldata)

    def generate(self) -> PackageResult:
        # Validate metadata?

        self.file_provider.create_directory(self.package_path)

        struct_maps = self.get_struct_maps()
        physical_struct_maps = [
            struct_map for struct_map in struct_maps
            if struct_map.type == StructMapType.physical
        ]
        if len(physical_struct_maps) != 1:
            self.clear_package_path()
            return self.get_package_result(
                success=False,
                message=(
                    "Expected to find a single \"structure:physical\" structure object " +
                    f"but found {len(physical_struct_maps)}"
                )
            )
        physical_struct_map = physical_struct_maps[0]

        missing_file_set_ids = []
        file_set_ids = []
        for struct_map_item in physical_struct_map.items:
            file_set_id = struct_map_item.file_set_id
            if self.file_sets_pending.pending(file_set_id=file_set_id):
                self.file_sets_pending.push(file_set_id=file_set_id, destination_path=self.package_path)
                file_set_ids.append(file_set_id)
            else:
                search_results = self.repository_client.search_for_file_set(file_set_id)
                if search_results:
                    file_set_ids.append(file_set_id)
                else:
                    missing_file_set_ids.append(file_set_id)

        if len(missing_file_set_ids) > 0:
            self.clear_package_path()
            return self.get_package_result(
                success=False,
                message=f"The following file sets were not found: {", ".join(missing_file_set_ids)}"
            )

        root_resource_path = self.package_path / self.root_resource_identifier
        self.file_provider.create_directory(root_resource_path)

        # Create root metadata files
        metadata_file_metadatas: list[FileMetadata] = []
        self.file_provider.create_directory(
            self.package_path / self.root_resource_identifier / "metadata"
        )
        try:
            descriptive_data = self.get_metadata_file_data(use="function:source")
            descriptive_file_path = self.get_metadata_file_path(".function:source.json")
            descriptive_file_metadata = self.get_file_metadata(
                file_path=descriptive_file_path, metadata_data=descriptive_data)
            self.create_root_metadata_file(
                file_path=descriptive_file_path,
                data=descriptive_data["data"],
                serializer=lambda x: json.dumps(x, indent=4)
            )
            metadata_file_metadatas.append(descriptive_file_metadata)

            common_data = self.get_metadata_file_data(use="function:service")
            common_file_path = self.get_metadata_file_path(".function:service.json")
            common_file_metadata = self.get_file_metadata(file_path=common_file_path, metadata_data=common_data)
            self.create_root_metadata_file(
                file_path=common_file_path,
                data=common_data["data"],
                serializer=lambda x: json.dumps(x, indent=4)
            )
            metadata_file_metadatas.append(common_file_metadata)

            provenance_data = self.get_metadata_file_data(use="function:provenance")
            provenance_file_path = self.get_metadata_file_path(".function:provenance.premis.xml")
            provenance_file_metadata = self.get_file_metadata(
                file_path=provenance_file_path, metadata_data=provenance_data)
            self.create_root_metadata_file(
                file_path=provenance_file_path,
                data=provenance_data["data"],
                serializer=serialize_provenance
            )
            metadata_file_metadatas.append(provenance_file_metadata)
        except PackageMetadataError as error:
            self.clear_package_path()
            return self.get_package_result(success=False, message=error.message)

        event_file_path = self.get_metadata_file_path(".function:event.premis.xml")
        (self.package_path / event_file_path).write_text(
            PreservationEventSerializer(self.create_ingest_event()).serialize()
        )
        metadata_file_metadatas.append(
            self.create_ingest_event_file_metadata(event_file_path)
        )

        alternate_identifier = provenance_data["data"]["alternate_identifier"]
        resource = PackageResource(
            id=uuid.UUID(self.root_resource_identifier),
            type=self.type,
            root=True,
            alternate_identifiers=[AlternateIdentifier(
                id=alternate_identifier, type="DLXS"
            )],
            events=[],
            metadata_files=metadata_file_metadatas,
            data_files=[],
            struct_maps=struct_maps
        )
        self.create_root_descriptor_file(resource, file_set_ids)

        dor_info = {
            "Action": "store",
            "Deposit-Group-Identifier": self.deposit_group.identifier,
            "Deposit-Group-Date": self.deposit_group.date,
            "Root-Identifier": self.root_resource_identifier,
            "Identifier": file_set_ids,
        }
        bag = BagAdapter.make(self.package_path, self.file_provider)
        bag.add_dor_info(dor_info=dor_info)

        return self.get_package_result(success=True, message="Generated package successfully!")
