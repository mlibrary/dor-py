import hashlib
import shutil
import tempfile
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from dor.adapters.generate_service_variant import generate_service_variant, ServiceImageProcessingError
from dor.adapters.make_intermediate_file import make_intermediate_file
from dor.adapters.technical_metadata import (
    ImageMimetype, ImageTechnicalMetadata, JHOVEDocError
)
from dor.builders.parts import FileInfo, MetadataFileInfo, UseFunction, UseFormat, flatten_use
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.models import (
    Agent, AlternateIdentifier, FileReference, PackageResource, FileMetadata, PreservationEvent
)
from dor.providers.serializers import PreservationEventSerializer
from dor.providers.utilities import sanitize_basename
from dor.settings import template_env


ACCEPTED_IMAGE_MIMETYPES = [
    ImageMimetype.JPEG,
    ImageMimetype.TIFF,
    ImageMimetype.JP2
]


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
    tech_metadata_file_info: MetadataFileInfo
    source_file_info: FileInfo | None = None


def create_preservation_event(
    type: str,
    collection_manager_email: str,
    detail: str = ""
):
    event = PreservationEvent(
        identifier=str(uuid.uuid4()),
        type=type,
        datetime=datetime.now(tz=UTC),
        detail=detail,
        agent=Agent(
            role="image_processing",
            address=collection_manager_email
        )
    )
    return event


class TransformerError(Exception):
    pass


class Transformer(ABC):

    @property
    @abstractmethod
    def metadata_file_infos(self) -> list[MetadataFileInfo]:
        raise NotImplementedError

    @abstractmethod
    def get_file_info_associations(self, source_file_info) -> list[FileInfoAssociation]:
        raise NotImplementedError

    @abstractmethod
    def transform(self, source_path: Path, source_tech_metadata: ImageTechnicalMetadata, collection_manager_email: str) -> None:
        raise NotImplementedError


class ServiceImageTransformer(Transformer):

    def __init__(
        self,
        file_set_directory: Path,
        file_set_identifier: FileSetIdentifier,
        generate_service_variant: Callable[[Path, Path], None]
    ):
        self.file_set_directory = file_set_directory
        self.file_set_identifier = file_set_identifier
        self.generate_service_variant = generate_service_variant

        self.file_info = FileInfo(
            identifier=self.file_set_identifier.identifier,
            basename=self.file_set_identifier.basename,
            uses=[UseFunction.service, UseFormat.image],
            mimetype=ImageMimetype.JP2.value
        )
        self.file_path = file_set_directory / self.file_info.path

        self.event_metadata_file_info = self.file_info.metadata(use=UseFunction.event, mimetype="text/xml+premis")

    @property
    def metadata_file_infos(self) -> list[MetadataFileInfo]:
        return [self.tech_metadata_file_info, self.event_metadata_file_info]

    def get_file_info_associations(self, source_file_info) -> list[FileInfoAssociation]:
        return [FileInfoAssociation(
            file_info=self.file_info,
            tech_metadata_file_info=self.tech_metadata_file_info,
            source_file_info=source_file_info
        )]

    def create_event(self, collection_manager_email: str) -> None:
        event = create_preservation_event("generate service derivative", collection_manager_email)
        event_xml = PreservationEventSerializer(event).serialize()
        (self.file_set_directory / self.event_metadata_file_info.path).write_text(event_xml)

    def create_technical_metadata(self) -> None:
        try:
            self.tech_metadata = ImageTechnicalMetadata.create(self.file_path)
        except JHOVEDocError:
            raise TransformerError

        self.tech_metadata_file_info = self.file_info.metadata(
            use=UseFunction.technical, mimetype=self.tech_metadata.metadata_mimetype.value
        )
        (self.file_set_directory / self.tech_metadata_file_info.path).write_text(str(self.tech_metadata))

    def create_service_file(self, source_path: Path, source_tech_metadata: ImageTechnicalMetadata):
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=".tiff")
        with temp_file:
            if source_tech_metadata.compressed or source_tech_metadata.rotated:
                compressible_file_path = Path(temp_file.name)
                make_intermediate_file(source_path, compressible_file_path)
            else:
                compressible_file_path = source_path

            try:
                generate_service_variant(compressible_file_path, self.file_path)
            except ServiceImageProcessingError:
                raise TransformerError

    def transform(
        self,
        source_path: Path,
        source_tech_metadata: ImageTechnicalMetadata,
        collection_manager_email: str
    ) -> None:
        self.create_service_file(source_path=source_path, source_tech_metadata=source_tech_metadata)
        self.create_event(collection_manager_email)
        self.create_technical_metadata()


def convert_metadata_file_info_to_file_metadata(metadata_file_info: MetadataFileInfo) -> FileMetadata:
    return FileMetadata(
        id=metadata_file_info.xmlid,
        use=flatten_use(*metadata_file_info.uses),
        ref=FileReference(
            locref=metadata_file_info.locref,
            mimetype=metadata_file_info.mimetype,
            mdtype=metadata_file_info.mdtype
        )
    )


def create_file_set_descriptor_data(resource: PackageResource) -> str:
    entity_template = template_env.get_template("preservation_mets.xml")
    xmldata = entity_template.render(
        resource=resource,
        object_identifier=resource.id,
        create_date=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    return xmldata


def create_file_set_directories(file_set_directory: Path) -> None:
    file_provider = FilesystemFileProvider()
    file_provider.create_directory(file_set_directory)
    file_provider.create_directory(file_set_directory / "data")
    file_provider.create_directory(file_set_directory / "metadata")
    file_provider.create_directory(file_set_directory / "descriptor")


def get_source_file_info(
    file_set_identifier: FileSetIdentifier, tech_metadata: ImageTechnicalMetadata
) -> FileInfo:
    return FileInfo(
        identifier=file_set_identifier.identifier,
        basename=file_set_identifier.basename,
        uses=[UseFunction.source, UseFormat.image],
        mimetype=tech_metadata.mimetype.value
    )


def copy_source_file(source_path: Path, destination_path: Path) -> None:
    shutil.copyfile(source_path, destination_path)


def get_event_file_info(file_info: FileInfo):
    return file_info.metadata(use=UseFunction.event, mimetype="text/xml+premis")


def create_package_resource(
    file_set_identifier: FileSetIdentifier,
    metadata_file_infos: list[MetadataFileInfo],
    file_info_associations: list[FileInfoAssociation]
) -> PackageResource:
    file_metadatas = []
    for file_info_association in file_info_associations:
        file_metadatas.append(FileMetadata(
            id=file_info_association.file_info.xmlid,
            use=flatten_use(*file_info_association.file_info.uses),
            groupid=file_info_association.source_file_info.xmlid if file_info_association.source_file_info is not None else None,
            mdid=file_info_association.tech_metadata_file_info.xmlid,
            ref=FileReference(
                locref=file_info_association.file_info.locref,
                mimetype=file_info_association.file_info.mimetype
            )
        ))

    resource = PackageResource(
        id=file_set_identifier.uuid,
        type="File Set",
        alternate_identifier=AlternateIdentifier(id=file_set_identifier.alternate_identifier, type="DLXS"),
        events=[],
        metadata_files=[
            convert_metadata_file_info_to_file_metadata(metadata_file_info)
            for metadata_file_info in metadata_file_infos
        ],
        data_files=file_metadatas
    )
    return resource


def process_basic_image(
    file_set_identifier: FileSetIdentifier,
    image_path: Path,
    output_path: Path,
    transformers: list[Transformer],
    collection_manager_email: str = "example@org.edu"
) -> bool:
    file_set_directory = output_path / file_set_identifier.identifier
    create_file_set_directories(file_set_directory)

    # Source
    try:
        source_tech_metadata = ImageTechnicalMetadata.create(image_path)
    except JHOVEDocError:
        return False

    if source_tech_metadata.mimetype not in ACCEPTED_IMAGE_MIMETYPES:
        return False

    source_file_info = get_source_file_info(file_set_identifier, source_tech_metadata)
    source_file_path = file_set_directory / source_file_info.path
    source_event_metadata_file_info = get_event_file_info(source_file_info)

    copy_source_file(source_path=image_path, destination_path=source_file_path)

    source_event = create_preservation_event("copy source image", collection_manager_email)
    source_event_xml = PreservationEventSerializer(source_event).serialize()
    (file_set_directory / source_event_metadata_file_info.path).write_text(source_event_xml)

    source_tech_metadata_file_info = source_file_info.metadata(
        use=UseFunction.technical, mimetype=source_tech_metadata.metadata_mimetype.value
    )
    (file_set_directory / source_tech_metadata_file_info.path).write_text(str(source_tech_metadata))

    # Transformations
    for transformer in transformers:
        try:
            transformer.transform(
                source_path=source_file_path,
                source_tech_metadata=source_tech_metadata,
                collection_manager_email=collection_manager_email
            )
        except TransformerError:
            return False

    metadata_file_infos = [source_tech_metadata_file_info, source_event_metadata_file_info]
    for transformer in transformers:
        metadata_file_infos += transformer.metadata_file_infos

    file_info_associations = [
        FileInfoAssociation(
            file_info=source_file_info,
            tech_metadata_file_info=source_tech_metadata_file_info,
        )
    ]
    for transformer in transformers:
        file_info_associations.extend(transformer.get_file_info_associations(source_file_info))

    resource = create_package_resource(
        file_set_identifier=file_set_identifier,
        metadata_file_infos=metadata_file_infos,
        file_info_associations=file_info_associations
    )
    descriptor_xml = create_file_set_descriptor_data(resource)
    descriptor_file_path = file_set_directory / "descriptor" / f"{file_set_identifier.identifier}.file_set.mets2.xml"
    with (descriptor_file_path).open("w") as file:
        file.write(descriptor_xml)

    return True
