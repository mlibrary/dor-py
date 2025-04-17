import hashlib
import shutil
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, Any
from functools import partial

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

NOP_RETURN = (None, None, None, None)

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

class TransformerError(Exception):
    pass

@dataclass
class Result:
    file_path: Path
    tech_metadata: ImageTechnicalMetadata
    file_info: FileInfo
    event: PreservationEvent


@dataclass
class Transformer:
    file_set_identifier: FileSetIdentifier
    file_set_directory: Path
    collection_manager_email: str
    steps: list[tuple[Callable, list[UseFormat | UseFunction]]] = field(default_factory=list)
    files: list[tuple[Path, ImageTechnicalMetadata, list[UseFormat | UseFunction]]] = field(default_factory=list)

    def add(self, method: Callable, uses=list[UseFormat | UseFunction]):
        self.steps.append((method, uses))

    def run(self):
        while self.steps:
            (method, uses) = self.steps.pop(0)
            result = method(transformer=self, uses=uses)
            if result:
                if not result.tech_metadata.valid:
                    raise TransformerError("a problem occurred")

                self.files.append(result)

    def write(self):
        # write metadata files
        metadata_file_infos = []
        file_info_associations = []
        for result in self.files:

            ( file_info, tech_metadata, file_info, event ) = (
                result.file_info,
                result.tech_metadata,
                result.file_info,
                result.event
            )

            if UseFunction.intermediate in file_info.uses:
                # don't persist these
                continue

            tech_metadata_file_info = file_info.metadata(
                use=UseFunction.technical, mimetype=tech_metadata.metadata_mimetype.value
            )
            (self.file_set_directory / tech_metadata_file_info.path).write_text(str(tech_metadata))

            event_metadata_file_info = get_event_file_info(file_info)
            event_xml = PreservationEventSerializer(event).serialize()
            (self.file_set_directory / event_metadata_file_info.path).write_text(event_xml)

            metadata_file_infos.append(tech_metadata_file_info)
            metadata_file_infos.append(event_metadata_file_info)

            file_info_associations.append(FileInfoAssociation(
                file_info=file_info,
                tech_metadata_file_info=tech_metadata_file_info
            ))

        # write descriptor file
        resource = create_package_resource(
            file_set_identifier=self.file_set_identifier,
            metadata_file_infos=metadata_file_infos,
            file_info_associations=file_info_associations
        )
        descriptor_xml = create_file_set_descriptor_data(resource)
        descriptor_file_path = self.file_set_directory / "descriptor" / f"{self.file_set_identifier.identifier}.file_set.mets2.xml"
        with (descriptor_file_path).open("w") as file:
            file.write(descriptor_xml)


    def get_file(self, function: list[UseFunction], format: UseFormat):
        for use in function:
            for result in self.files:
                if use in result.file_info.uses and format in result.file_info.uses:
                    return result
        return False


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


def get_service_file_info(file_set_identifier: FileSetIdentifier) -> FileInfo:
    return FileInfo(
        identifier=file_set_identifier.identifier,
        basename=file_set_identifier.basename,
        uses=[UseFunction.service, UseFormat.image],
        mimetype=ImageMimetype.JP2.value
    )


def process_source_file(image_path: Path, transformer: Transformer, uses: list[Any]):
    try:
        source_tech_metadata = ImageTechnicalMetadata.create(image_path)
    except JHOVEDocError:
        return None

    # source_file_info = get_source_file_info(transformer.file_set_identifier, source_tech_metadata)
    file_info = FileInfo(
        identifier=transformer.file_set_identifier.identifier,
        basename=transformer.file_set_identifier.basename,
        uses=uses,
        mimetype=source_tech_metadata.mimetype.value
    )

    source_file_path = transformer.file_set_directory / file_info.path
    copy_source_file(source_path=image_path, destination_path=source_file_path)

    event = create_preservation_event("copy source file", transformer.collection_manager_email)

    return Result(source_file_path, source_tech_metadata, file_info, event)

def check_source_orientation(transformer: Transformer, uses: list[Any]):
    source_file_result = transformer.get_file(function=[UseFunction.source], format=UseFormat.image)
    if source_file_result.file_path is None:
        return None

    if not source_file_result.tech_metadata.rotated:
        return None    

    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=".tiff")
    compressible_file_path = Path(temp_file.name)
    make_intermediate_file(source_file_result.file_path, compressible_file_path)

    try:
        tech_metadata = ImageTechnicalMetadata.create(compressible_file_path)
    except JHOVEDocError:
        return None

    file_info = FileInfo(
        identifier=transformer.file_set_identifier.identifier,
        basename=transformer.file_set_identifier.basename,
        uses=uses,
        mimetype=tech_metadata.mimetype.value
    )
    
    return Result(compressible_file_path, tech_metadata, file_info, None)


def copy_source_file(source_path: Path, destination_path: Path) -> None:
    shutil.copyfile(source_path, destination_path)
    


def get_event_file_info(file_info: FileInfo):
    return file_info.metadata(use=UseFunction.event, mimetype="text/xml+premis")

def process_service_file(transformer: Transformer, uses: list[Any]):
    source_file_result = transformer.get_file(function=[UseFunction.intermediate, UseFunction.source], format=UseFormat.image)

    file_info = FileInfo(
        identifier=transformer.file_set_identifier.identifier,
        basename=transformer.file_set_identifier.basename,
        uses=uses,
        mimetype=ImageMimetype.JP2.value
    )

    service_file_path = transformer.file_set_directory / file_info.path
    try:
        create_service_file(
            source_path=source_file_result.file_path,
            destination_path=service_file_path,
            tech_metadata=source_file_result.tech_metadata,
            generate_service_variant=generate_service_variant
        )
    except ServiceImageProcessingError:
        return None
    
    try:
        service_tech_metadata = ImageTechnicalMetadata.create(service_file_path)
    except JHOVEDocError:
        return None

    event = create_preservation_event("create JPEG2000 service file", transformer.collection_manager_email)

    return Result(service_file_path, service_tech_metadata, file_info, event)

def create_service_file(
    source_path: Path,
    destination_path: Path,
    tech_metadata: ImageTechnicalMetadata,
    generate_service_variant: Callable[[Path, Path], None]
) -> None:
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=".tiff")
    with temp_file:
        if tech_metadata.compressed or tech_metadata.rotated:
            compressible_file_path = Path(temp_file.name)
            make_intermediate_file(source_path, compressible_file_path)
        else:
            compressible_file_path = source_path

        generate_service_variant(compressible_file_path, destination_path)


@dataclass
class FileInfoAssociation:
    file_info: FileInfo
    tech_metadata_file_info: MetadataFileInfo
    source_file_info: FileInfo | None = None


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
    collection_manager_email: str = "example@org.edu",
    generate_service_variant: Callable[[Path, Path], None] = generate_service_variant
) -> bool:
    file_set_directory = output_path / file_set_identifier.identifier
    create_file_set_directories(file_set_directory)

    transformer = Transformer(
        file_set_identifier=file_set_identifier, 
        file_set_directory=file_set_directory,
        collection_manager_email=collection_manager_email
    )
    transformer.add(partial(process_source_file, image_path), uses=[UseFunction.source, UseFormat.image])
    # transformer.add(partial(process_source_file, transcription_path), uses=[UseFunction.source, UseFunction.service, UseFormat.text])

    transformer.add(check_source_orientation, uses=[UseFunction.intermediate])
    transformer.add(process_service_file, uses=[UseFunction.service, UseFormat.image])

    transformer.run()
    transformer.write()
    return True


