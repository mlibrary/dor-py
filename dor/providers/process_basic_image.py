import shutil
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable

from dor.adapters.generate_service_variant import generate_service_variant, ServiceImageProcessingError
from dor.adapters.make_intermediate_file import make_intermediate_file
from dor.adapters.technical_metadata import (
    ImageMimetype, TechnicalMetadata, TechnicalMetadataError, get_technical_metadata
)
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.builders.parts import FileInfo, UseFunction, UseFormat, flatten_use
from dor.providers.models import (
    Agent, AlternateIdentifier, FileReference, PackageResource, FileMetadata, PreservationEvent
)
from dor.providers.serializers import PreservationEventSerializer
from dor.settings import template_env


ACCEPTED_IMAGE_MIMETYPES = [
    ImageMimetype.JPEG,
    ImageMimetype.TIFF,
    ImageMimetype.JP2
]

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


def create_file_set_descriptor_file(
    resource: PackageResource,
    descriptor_file_path: Path
) -> None:

    entity_template = template_env.get_template("preservation_mets.xml")
    xmldata = entity_template.render(
        resource=resource,
        object_identifier=resource.id,
        create_date=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
    with (descriptor_file_path).open("w") as file:
        file.write(xmldata)

def process_basic_image(
    identifier: str,
    input_image_path: Path,
    output_path: Path,
    collection_manager_email: str = "example@org.edu",
    get_technical_metadata: Callable[[Path], TechnicalMetadata] = get_technical_metadata,
    generate_service_variant: Callable[[Path, Path], None] = generate_service_variant
) -> bool:
    file_provider = FilesystemFileProvider()
    file_provider.create_directory(output_path / identifier)
    file_provider.create_directory(output_path / identifier / "data")
    file_provider.create_directory(output_path / identifier / "metadata")
    file_provider.create_directory(output_path / identifier / "descriptor")

    source_file_path = input_image_path
    basename = source_file_path.stem

    try:
        source_tech_metadata = get_technical_metadata(source_file_path)
    except TechnicalMetadataError:
        return False

    if source_tech_metadata.mimetype not in ACCEPTED_IMAGE_MIMETYPES:
        return False

    image_file_info = FileInfo(
        identifier, basename, [UseFunction.source, UseFormat.image], source_tech_metadata.mimetype.value
    )
    new_source_file_path = output_path / identifier / image_file_info.path
    shutil.copyfile(source_file_path, new_source_file_path)

    source_event = create_preservation_event("copy source image", collection_manager_email)
    source_event_xml = PreservationEventSerializer(source_event).serialize()
    source_event_metadata_file_info = image_file_info.metadata(UseFunction.event, "text/xml+premis")
    (output_path / identifier / source_event_metadata_file_info.path).write_text(source_event_xml)

    tech_meta_file_info = image_file_info.metadata(
        UseFunction.technical, source_tech_metadata.metadata_mimetype.value
    )
    (output_path / identifier / tech_meta_file_info.path).write_text(source_tech_metadata.metadata)

    service_image_file_info = FileInfo(
        identifier, basename, [UseFunction.service, UseFormat.image], ImageMimetype.JP2.value
    )
    service_file_path = output_path / identifier / service_image_file_info.path

    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=".tiff")
    with temp_file:
        if source_tech_metadata.compressed or source_tech_metadata.rotated:
            compressible_file_path = Path(temp_file.name)
            make_intermediate_file(new_source_file_path, compressible_file_path)
        else:
            compressible_file_path = new_source_file_path

        try:
            generate_service_variant(compressible_file_path, service_file_path)
        except ServiceImageProcessingError:
            return False

    service_event = create_preservation_event("generate service derivative", collection_manager_email)
    service_event_xml = PreservationEventSerializer(service_event).serialize()
    service_event_metadata_file_info = service_image_file_info.metadata(UseFunction.event, "text/xml+premis")
    (output_path / identifier / service_event_metadata_file_info.path).write_text(service_event_xml)

    try:
        service_tech_metadata = get_technical_metadata(service_file_path)
    except TechnicalMetadataError as error:
        return False

    service_tech_meta_file_info = service_image_file_info.metadata(
        UseFunction.technical, service_tech_metadata.metadata_mimetype.value
    )
    (output_path / identifier / service_tech_meta_file_info.path).write_text(service_tech_metadata.metadata)

    descriptor_file_path = output_path / identifier / "descriptor" / f"{identifier}.file_set.mets2.xml"

    resource = PackageResource(
        id=uuid.UUID(identifier),
        type="File Set",
        alternate_identifier=AlternateIdentifier(id=basename, type="DLXS"),
        events=[],
        metadata_files=[
            FileMetadata(
                id=tech_meta_file_info.xmlid,
                use=flatten_use(*tech_meta_file_info.uses),
                ref=FileReference(
                    locref=tech_meta_file_info.locref,
                    mimetype=tech_meta_file_info.mimetype,
                    mdtype=tech_meta_file_info.mdtype
                )
            ),
            FileMetadata(
                id=service_tech_meta_file_info.xmlid,
                use=flatten_use(*service_tech_meta_file_info.uses),
                ref=FileReference(
                    locref=service_tech_meta_file_info.locref,
                    mimetype=service_tech_meta_file_info.mimetype,
                    mdtype=service_tech_meta_file_info.mdtype
                )
            ),
            FileMetadata(
                id=source_event_metadata_file_info.xmlid,
                use=flatten_use(*source_event_metadata_file_info.uses),
                ref=FileReference(
                    locref=source_event_metadata_file_info.locref,
                    mimetype=source_event_metadata_file_info.mimetype,
                    mdtype=source_event_metadata_file_info.mdtype
                )
            ),
            FileMetadata(
                id=service_event_metadata_file_info.xmlid,
                use=flatten_use(*service_event_metadata_file_info.uses),
                ref=FileReference(
                    locref=service_event_metadata_file_info.locref,
                    mimetype=service_event_metadata_file_info.mimetype,
                    mdtype=service_event_metadata_file_info.mdtype
                )
            ),

        ],
        data_files=[
            FileMetadata(
                id=image_file_info.xmlid,
                use=flatten_use(*image_file_info.uses),
                mdid=tech_meta_file_info.xmlid,
                ref=FileReference(
                    locref=image_file_info.locref,
                    mimetype=image_file_info.mimetype
                )
            ),
            FileMetadata(
                id=service_image_file_info.xmlid,
                use=flatten_use(*service_image_file_info.uses),
                groupid=image_file_info.xmlid,
                mdid=service_tech_meta_file_info.xmlid,
                ref=FileReference(
                    locref=service_image_file_info.locref,
                    mimetype=service_image_file_info.mimetype
                )
            ),
        ]
    )

    create_file_set_descriptor_file(resource, descriptor_file_path)

    return True
