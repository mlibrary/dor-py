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
    ImageTechnicalMetadata, JHOVEDocError, Mimetype
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
    Mimetype.JPEG,
    Mimetype.TIFF,
    Mimetype.JP2
]

NOP_RETURN = (None, None, None)

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
class Transformer:
    file_set_identifier: FileSetIdentifier
    file_set_directory: Path
    steps: list[tuple[Callable, list[UseFormat | UseFunction]]] = field(default_factory=list)
    files: list[tuple[Path, ImageTechnicalMetadata, list[UseFormat | UseFunction]]] = field(default_factory=list)

    def add(self, method: Callable, uses=list[UseFormat | UseFunction]):
        self.steps.append((method, uses))

    def run(self):
        while self.steps:
            (method, uses) = self.steps.pop(0)
            (path, tech_metadata, file_info) = method(transformer=self, uses=uses)
            if path:
                if not tech_metadata.valid:
                    raise TransformerError("a problem occurred")

                self.files.append((path, tech_metadata, file_info))

    def write(self):
        # write metadata files
        for ( file_path, tech_metadata, file_info ) in self.files:
            if UseFunction.intermediate in file_info.uses:
                # don't persist these
                continue

            tech_metadata_file_info = file_info.metadata(
                use=UseFunction.technical, mimetype=tech_metadata.metadata_mimetype.value
            )
            (self.file_set_directory / tech_metadata_file_info.path).write_text(str(tech_metadata))


    def get_file(self, uses: list[UseFunction]):
        for use in uses:
            for file_ in self.files:
                if use in file_[-1].uses:
                    return file_
        return NOP_RETURN


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
        mimetype=Mimetype.JP2.value
    )


def process_source_file(image_path: Path, transformer: Transformer, uses: list[Any]):
    try:
        source_tech_metadata = ImageTechnicalMetadata.create(image_path)
    except JHOVEDocError:
        return NOP_RETURN

    # source_file_info = get_source_file_info(transformer.file_set_identifier, source_tech_metadata)
    file_info = FileInfo(
        identifier=transformer.file_set_identifier.identifier,
        basename=transformer.file_set_identifier.basename,
        uses=uses,
        mimetype=source_tech_metadata.mimetype.value
    )

    source_file_path = transformer.file_set_directory / file_info.path
    copy_source_file(source_path=image_path, destination_path=source_file_path)

    return (source_file_path, source_tech_metadata, file_info)

def check_source_orientation(transformer: Transformer, uses: list[Any]):
    (image_path, tech_metadata, file_info) = transformer.get_file(uses=[UseFunction.source])
    if image_path is None:
        print("well that's a problem")
        return NOP_RETURN
    if tech_metadata.rotated:
        print("we must rotate")
    
    print("everything's fine, keep going")
    return ( None, None, None )

def copy_source_file(source_path: Path, destination_path: Path) -> None:
    shutil.copyfile(source_path, destination_path)
    


def get_event_file_info(file_info: FileInfo):
    return file_info.metadata(use=UseFunction.event, mimetype="text/xml+premis")

def process_service_file(transformer: Transformer, uses: list[Any]):
    (image_path, tech_metadata, file_info) = transformer.get_file(uses=[UseFunction.intermediate, UseFunction.source])

    file_info = FileInfo(
        identifier=transformer.file_set_identifier.identifier,
        basename=transformer.file_set_identifier.basename,
        uses=uses,
        mimetype=ImageMimetype.JP2.value
    )

    service_file_path = transformer.file_set_directory / file_info.path
    try:
        create_service_file(
            source_path=image_path,
            destination_path=service_file_path,
            tech_metadata=tech_metadata,
            generate_service_variant=generate_service_variant
        )
    except ServiceImageProcessingError:
        return NOP_RETURN
    
    try:
        service_tech_metadata = ImageTechnicalMetadata.create(service_file_path)
    except JHOVEDocError:
        return NOP_RETURN

    return ( service_file_path, service_tech_metadata, file_info )

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

    transformer = Transformer(file_set_identifier=file_set_identifier, file_set_directory=file_set_directory)
    transformer.add(partial(process_source_file, image_path), uses=[UseFunction.source, UseFormat.image])
    transformer.add(check_source_orientation, uses=[UseFunction.intermediate])
    transformer.add(process_service_file, uses=[UseFunction.service, UseFormat.image])

    transformer.run()
    transformer.write()
    return True

def old_process_basic_image():

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

    service_file_info = get_service_file_info(file_set_identifier)
    service_file_path = file_set_directory / service_file_info.path
    service_event_metadata_file_info = get_event_file_info(service_file_info)

    try:
        create_service_file(
            source_path=source_file_path,
            destination_path=service_file_path,
            tech_metadata=source_tech_metadata,
            generate_service_variant=generate_service_variant
        )
    except ServiceImageProcessingError:
        return False

    service_event = create_preservation_event("generate service derivative", collection_manager_email)
    service_event_xml = PreservationEventSerializer(service_event).serialize()
    (file_set_directory / service_event_metadata_file_info.path).write_text(service_event_xml)

    try:
        service_tech_metadata = ImageTechnicalMetadata.create(service_file_path)
    except JHOVEDocError:
        return False

    service_tech_metadata_file_info = service_file_info.metadata(
        use=UseFunction.technical, mimetype=service_tech_metadata.metadata_mimetype.value
    )
    (file_set_directory / service_tech_metadata_file_info.path).write_text(str(service_tech_metadata))

    resource = create_package_resource(
        file_set_identifier=file_set_identifier,
        metadata_file_infos=[
            source_tech_metadata_file_info,
            source_event_metadata_file_info,
            service_tech_metadata_file_info,
            service_event_metadata_file_info
        ],
        file_info_associations=[
            FileInfoAssociation(
                file_info=source_file_info,
                tech_metadata_file_info=source_tech_metadata_file_info,
            ),
            FileInfoAssociation(
                file_info=service_file_info,
                tech_metadata_file_info=service_tech_metadata_file_info,
                source_file_info=source_file_info
            )
        ]
    )
    descriptor_xml = create_file_set_descriptor_data(resource)
    descriptor_file_path = file_set_directory / "descriptor" / f"{file_set_identifier.identifier}.file_set.mets2.xml"
    with (descriptor_file_path).open("w") as file:
        file.write(descriptor_xml)

    return True
