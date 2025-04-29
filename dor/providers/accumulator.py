import uuid
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Self

from dor.adapters.technical_metadata import TechnicalMetadata
from dor.builders.parts import (
    FileInfo,
    flatten_use,
    MetadataFileInfo, 
    UseFormat,
    UseFunction
)
from dor.providers.models import (
    AlternateIdentifier,
    FileMetadata,
    FileReference,
    PackageResource,
    PreservationEvent,
)
from dor.providers.serializers import PreservationEventSerializer
from dor.providers.utilities import sanitize_basename
from dor.settings import template_env


class FileSetIdentifier:

    def __init__(self, project_id: str, file_name: str):
        self.project_id = project_id
        self.file_name = file_name
        self.basename = sanitize_basename(Path(file_name).stem)

    @property
    def alternate_identifier(self) -> str:
        return f"{self.project_id}:{self.basename}"

    @property
    def uuid(self) -> uuid.UUID:
        hex_string = hashlib.md5(self.alternate_identifier.encode("UTF-8")).hexdigest()
        return uuid.UUID(hex=hex_string)

    @property
    def identifier(self) -> str:
        return str(self.uuid)


@dataclass
class FileInfoAssociation:
    file_info: FileInfo
    tech_metadata_file_info: FileInfo
    source_file_info: FileInfo | None = None


@dataclass
class ResultFile:
    file_path: Path
    tech_metadata: TechnicalMetadata
    file_info: FileInfo
    event: PreservationEvent
    source_file_result: Self | None = None

    @property
    def association(self) -> FileInfoAssociation:
        return FileInfoAssociation(
            file_info=self.file_info,
            tech_metadata_file_info=self.file_info.metadata(
                use=UseFunction.technical,
                mimetype=self.tech_metadata.metadata_mimetype.value,
            ),
            source_file_info=self.source_file_result.file_info if self.source_file_result else None
        )


class AccumulatorError(Exception):
    pass


@dataclass
class Accumulator:
    file_set_identifier: FileSetIdentifier
    file_set_directory: Path
    collection_manager_email: str
    result_files: list[ResultFile] = field(default_factory=list)

    def add_file(self, file: ResultFile):
        self.result_files.append(file)

    def get_file(self, function: list[UseFunction], format: UseFormat):
        for use in function:
            for result in self.result_files:
                if (
                    use in result.file_info.uses
                    and format in result.file_info.uses
                ):
                    return result
        raise AccumulatorError(
            f"Result file not found for function {[str(use) for use in function]} and format {format}"
        )

    def write(self):
        # write metadata files
        metadata_file_infos = []
        file_info_associations = []
        for result in self.result_files:

            (file_info, tech_metadata, file_info, event) = (
                result.file_info,
                result.tech_metadata,
                result.file_info,
                result.event,
            )

            if event:
                event_metadata_file_info = get_event_file_info(file_info)
                event_xml = PreservationEventSerializer(event).serialize()
                (self.file_set_directory / event_metadata_file_info.path).write_text(
                    event_xml
                )
                metadata_file_infos.append(event_metadata_file_info)

            if UseFunction.intermediate in file_info.uses:
                # don't persist these
                continue

            tech_metadata_file_info = result.association.tech_metadata_file_info
            (self.file_set_directory / tech_metadata_file_info.path).write_text(
                str(tech_metadata)
            )

            metadata_file_infos.append(tech_metadata_file_info)
            file_info_associations.append(result.association)

        # write the descriptor file
        resource = create_package_resource(
            file_set_identifier=self.file_set_identifier,
            metadata_file_infos=metadata_file_infos,
            file_info_associations=file_info_associations,
        )
        descriptor_xml = create_file_set_descriptor_data(resource)
        descriptor_file_path = (
            self.file_set_directory
            / "descriptor"
            / f"{self.file_set_identifier.identifier}.file_set.mets2.xml"
        )
        with descriptor_file_path.open("w") as file:
            file.write(descriptor_xml)


def convert_metadata_file_info_to_file_metadata(
    metadata_file_info: MetadataFileInfo,
) -> FileMetadata:
    return FileMetadata(
        id=metadata_file_info.xmlid,
        use=flatten_use(*metadata_file_info.uses),
        ref=FileReference(
            locref=metadata_file_info.locref,
            mimetype=metadata_file_info.mimetype,
            mdtype=metadata_file_info.mdtype,
        ),
    )


def create_file_set_descriptor_data(resource: PackageResource) -> str:
    entity_template = template_env.get_template("preservation_mets.xml")
    xmldata = entity_template.render(
        resource=resource,
        object_identifier=resource.id,
        create_date=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    return xmldata


def get_event_file_info(file_info: FileInfo):
    return file_info.metadata(use=UseFunction.event, mimetype="text/xml+premis")


def create_package_resource(
    file_set_identifier: FileSetIdentifier,
    metadata_file_infos: list[MetadataFileInfo],
    file_info_associations: list[FileInfoAssociation],
) -> PackageResource:
    file_metadatas = []
    for file_info_association in file_info_associations:
        file_metadatas.append(
            FileMetadata(
                id=file_info_association.file_info.xmlid,
                use=flatten_use(*file_info_association.file_info.uses),
                groupid=(
                    file_info_association.source_file_info.xmlid
                    if file_info_association.source_file_info is not None
                    else None
                ),
                mdid=file_info_association.tech_metadata_file_info.xmlid,
                ref=FileReference(
                    locref=file_info_association.file_info.locref,
                    mimetype=file_info_association.file_info.mimetype,
                ),
            )
        )

    resource = PackageResource(
        id=file_set_identifier.uuid,
        type="File Set",
        alternate_identifier=AlternateIdentifier(
            id=file_set_identifier.alternate_identifier, type="DLXS"
        ),
        events=[],
        metadata_files=[
            convert_metadata_file_info_to_file_metadata(metadata_file_info)
            for metadata_file_info in metadata_file_infos
        ],
        data_files=file_metadatas,
    )
    return resource
