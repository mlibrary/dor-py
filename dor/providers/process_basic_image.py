from datetime import datetime
import shutil
from pathlib import Path
from typing import Callable

from dor.adapters.technical_metadata import TechnicalMetadata, TechnicalMetadataError, get_technical_metadata
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.builders.parts import FileInfo, UseFunction, UseFormat, flatten_use
from dor.providers.models import AlternateIdentifier, FileReference, PackageResource, FileMetadata
from dor.settings import template_env

ACCEPTED_IMAGE_MIMETYPES = [
    "image/jpeg",
    "image/tiff",
    "image/jp2",
]


class ServiceImageProcessingError(Exception):
    pass


def get_source_file_path(input_path: Path) -> Path:
    for file_path in input_path.iterdir():
        return file_path
    raise Exception()


def generate_fake_service_variant(source_file_path: Path, source_metadata: TechnicalMetadata, service_file_path: Path):
    shutil.copyfile(source_file_path, service_file_path)

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
    input_path: Path,
    output_path: Path,
    get_technical_metadata: Callable[[Path], TechnicalMetadata] = get_technical_metadata,
    generate_service_variant: Callable[[Path, TechnicalMetadata, Path], None] = generate_fake_service_variant
) -> bool:
    file_provider = FilesystemFileProvider()
    file_provider.create_directory(output_path / identifier)
    file_provider.create_directory(output_path / identifier / "data")
    file_provider.create_directory(output_path / identifier / "metadata")
    file_provider.create_directory(output_path / identifier / "descriptor")

    source_file_path = get_source_file_path(input_path)
    basename = source_file_path.stem

    try:
        source_tech_metadata = get_technical_metadata(source_file_path)
    except TechnicalMetadataError as error:
        return False

    if source_tech_metadata.mimetype not in ACCEPTED_IMAGE_MIMETYPES:
        return False

    image_file_info = FileInfo(
        identifier, basename, [UseFunction.source, UseFormat.image], source_tech_metadata.mimetype
    )
    new_source_file_path = output_path / identifier / image_file_info.path

    shutil.copyfile(source_file_path, new_source_file_path)

    tech_meta_file_info = image_file_info.metadata(UseFunction.technical, source_tech_metadata.metadata_mimetype)
    (output_path / identifier / tech_meta_file_info.path).write_text(source_tech_metadata.metadata)

    compressible_file_path = new_source_file_path
    # check source_tech_metadata for rotation
    # if true: 
    #    compressible_file_path = make_temp()
    #    generate_intermediate_file(new_source_file_path, compressible_file_path)

    service_image_file_info = FileInfo(
        identifier, basename, [UseFunction.service, UseFormat.image], "image/jpeg"
    )
    service_file_path = output_path / identifier / service_image_file_info.path

    try:
        # new_source_file_path -> compressible_file_path
        generate_service_variant(new_source_file_path, source_tech_metadata, service_file_path)
    except ServiceImageProcessingError as error:
        return False

    try:
        service_tech_metadata = get_technical_metadata(service_file_path)
    except TechnicalMetadataError as error:
        return False

    service_tech_meta_file_info = service_image_file_info.metadata(UseFunction.technical, service_tech_metadata.metadata_mimetype)
    (output_path / identifier / service_tech_meta_file_info.path).write_text(service_tech_metadata.metadata)

    descriptor_file_path = output_path / identifier / "descriptor" / f"{identifier}.file_set.mets2.xml"

    resource = PackageResource(
        id=identifier,
        type="File Set",
        alternate_identifier=AlternateIdentifier(id=basename, type="DLXS"),
        events=[],
        metadata_files=[
            FileMetadata(
                id=tech_meta_file_info.xmlid,
                use=flatten_use(*tech_meta_file_info.uses),
                ref=FileReference(
                    locref=tech_meta_file_info.locref,
                    mimetype=tech_meta_file_info.mimetype
                )
            ),
            FileMetadata(
                id=service_tech_meta_file_info.xmlid,
                use=flatten_use(*service_tech_meta_file_info.uses),
                ref=FileReference(
                    locref=service_tech_meta_file_info.locref,
                    mimetype=service_tech_meta_file_info.mimetype
                )
            )
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
