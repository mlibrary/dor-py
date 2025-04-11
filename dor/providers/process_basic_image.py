import hashlib
import shutil
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from dor.adapters.generate_service_variant import generate_service_variant, ServiceImageProcessingError
from dor.adapters.make_intermediate_file import make_intermediate_file
from dor.adapters.technical_metadata import (
    ImageMimetype, JHOVEDoc, JHOVEDocError
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


def process_basic_image(
    file_set_identifier: FileSetIdentifier,
    image_path: Path,
    output_path: Path,
    collection_manager_email: str = "example@org.edu",
    generate_service_variant: Callable[[Path, Path], None] = generate_service_variant
) -> bool:
    file_set_directory = output_path / file_set_identifier.identifier
    create_file_set_directories(file_set_directory)

    try:
        source_tech_metadata = JHOVEDoc.create(image_path).technical_metadata
    except JHOVEDocError:
        return False

    if source_tech_metadata.mimetype not in ACCEPTED_IMAGE_MIMETYPES:
        return False

    source_file_info = FileInfo(
        identifier=file_set_identifier.identifier,
        basename=file_set_identifier.basename,
        uses=[UseFunction.source, UseFormat.image],
        mimetype=source_tech_metadata.mimetype.value
    )
    source_file_path = file_set_directory / source_file_info.path
    shutil.copyfile(image_path, source_file_path)

    source_event = create_preservation_event("copy source image", collection_manager_email)
    source_event_xml = PreservationEventSerializer(source_event).serialize()
    source_event_metadata_file_info = source_file_info.metadata(
        use=UseFunction.event, mimetype="text/xml+premis"
    )
    (file_set_directory / source_event_metadata_file_info.path).write_text(source_event_xml)

    source_tech_metadata_file_info = source_file_info.metadata(
        use=UseFunction.technical, mimetype=source_tech_metadata.metadata_mimetype.value
    )
    (file_set_directory / source_tech_metadata_file_info.path).write_text(source_tech_metadata.metadata)

    service_file_info = FileInfo(
        identifier=file_set_identifier.identifier,
        basename=file_set_identifier.basename,
        uses=[UseFunction.service, UseFormat.image],
        mimetype=ImageMimetype.JP2.value
    )
    service_file_path = file_set_directory / service_file_info.path

    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=".tiff")
    with temp_file:
        if source_tech_metadata.compressed or source_tech_metadata.rotated:
            compressible_file_path = Path(temp_file.name)
            make_intermediate_file(source_file_path, compressible_file_path)
        else:
            compressible_file_path = source_file_path

        try:
            generate_service_variant(compressible_file_path, service_file_path)
        except ServiceImageProcessingError:
            return False

    service_event = create_preservation_event("generate service derivative", collection_manager_email)
    service_event_xml = PreservationEventSerializer(service_event).serialize()
    service_event_metadata_file_info = service_file_info.metadata(
        use=UseFunction.event, mimetype="text/xml+premis"
    )
    (file_set_directory / service_event_metadata_file_info.path).write_text(service_event_xml)

    try:
        service_tech_metadata = JHOVEDoc.create(service_file_path).technical_metadata
    except JHOVEDocError:
        return False

    service_tech_metadata_file_info = service_file_info.metadata(
        use=UseFunction.technical, mimetype=service_tech_metadata.metadata_mimetype.value
    )
    (file_set_directory / service_tech_metadata_file_info.path).write_text(service_tech_metadata.metadata)

    resource = PackageResource(
        id=file_set_identifier.uuid,
        type="File Set",
        alternate_identifier=AlternateIdentifier(id=file_set_identifier.alternate_identifier, type="DLXS"),
        events=[],
        metadata_files=[
            convert_metadata_file_info_to_file_metadata(source_tech_metadata_file_info),
            convert_metadata_file_info_to_file_metadata(source_event_metadata_file_info),
            convert_metadata_file_info_to_file_metadata(service_tech_metadata_file_info),
            convert_metadata_file_info_to_file_metadata(service_event_metadata_file_info)
        ],
        data_files=[
            FileMetadata(
                id=source_file_info.xmlid,
                use=flatten_use(*source_file_info.uses),
                mdid=source_tech_metadata_file_info.xmlid,
                ref=FileReference(
                    locref=source_file_info.locref,
                    mimetype=source_file_info.mimetype
                )
            ),
            FileMetadata(
                id=service_file_info.xmlid,
                use=flatten_use(*service_file_info.uses),
                groupid=source_file_info.xmlid,
                mdid=service_tech_metadata_file_info.xmlid,
                ref=FileReference(
                    locref=service_file_info.locref,
                    mimetype=service_file_info.mimetype
                )
            ),
        ]
    )
    descriptor_xml = create_file_set_descriptor_data(resource)
    descriptor_file_path = file_set_directory / "descriptor" / f"{file_set_identifier.identifier}.file_set.mets2.xml"
    with (descriptor_file_path).open("w") as file:
        file.write(descriptor_xml)

    return True
