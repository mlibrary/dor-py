from datetime import datetime
import shutil
from pathlib import Path
from typing import Callable

from dataclasses import dataclass
import uuid

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.builders.parts import FileInfo, UseFunction, UseFormat, flatten_use
from dor.providers.models import AlternateIdentifier, FileReference, PackageResource, FileMetadata
from dor.settings import template_env

class TechnicalMetadataError(Exception):
    pass

class ServiceImageProcessingError(Exception):
    pass

@dataclass
class TechnicalMetadata:
    # height: int
    # width: int
    mimetype: str
    metadata: str
    metadata_mimetype: str

    
def get_source_file_path(input_path: Path) -> Path:
    for file_path in input_path.iterdir():
        return file_path
    raise Exception()


def get_fake_technical_metadata(file_path: Path) -> TechnicalMetadata:
    return TechnicalMetadata(mimetype="image/jpeg", metadata=f"<xml>{file_path}</xml>", metadata_mimetype="text/xml+mix")

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
    get_technical_metadata: Callable[[Path], str] = get_fake_technical_metadata,
    generate_service_variant: Callable[[Path, TechnicalMetadata], Path] = generate_fake_service_variant
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

    image_file_info = FileInfo(
        identifier, basename, [UseFunction.source, UseFormat.image], source_tech_metadata.mimetype
    )
    new_source_file_path = output_path / identifier / image_file_info.path

    shutil.copyfile(source_file_path, new_source_file_path)

    tech_meta_file_info = image_file_info.metadata(UseFunction.technical, source_tech_metadata.metadata_mimetype)
    (output_path / identifier / tech_meta_file_info.path).write_text(source_tech_metadata.metadata)

    service_image_file_info = FileInfo(
        identifier, basename, [UseFunction.service, UseFormat.image], "image/jpeg"
    )
    service_file_path = output_path / identifier / service_image_file_info.path

    try:
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
                ## these ids need to be part of the file_info to
                ## refer to them in other FileMetadata
                id=uuid.uuid4(),
                use=flatten_use(*tech_meta_file_info.uses),
                ref=FileReference(
                    locref=tech_meta_file_info.locref,
                    mimetype=tech_meta_file_info.mimetype
                )
            ),
            FileMetadata(
                id=uuid.uuid4(),
                use=flatten_use(*service_tech_meta_file_info.uses),
                ref=FileReference(
                    locref=service_tech_meta_file_info.locref,
                    mimetype=service_tech_meta_file_info.mimetype
                )
            )
        ],
        data_files=[
            FileMetadata(
                id=uuid.uuid4(),
                use=flatten_use(*image_file_info.uses),
                ref=FileReference(
                    locref=image_file_info.locref,
                    mimetype=image_file_info.mimetype
                )
            ),
            FileMetadata(
                id=uuid.uuid4(),
                use=flatten_use(*service_image_file_info.uses),
                groupid=uuid.uuid4(),
                ref=FileReference(
                    locref=service_image_file_info.locref,
                    mimetype=service_image_file_info.mimetype
                )
            ),
        ]
    )

    create_file_set_descriptor_file(resource, descriptor_file_path)

    return True
