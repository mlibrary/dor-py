import shutil
from pathlib import Path
from typing import Callable

from dataclasses import dataclass

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.builders.parts import FileInfo, UseFunction, UseFormat


class TechnicalMetadataError(Exception):
    pass

@dataclass
class FileMetaData:
    # height: int
    # width: int
    mimetype: str
    metadata: str
    metadata_mimetype: str

    
def get_source_file_path(input_path: Path) -> Path:
    for file_path in input_path.iterdir():
        return file_path
    raise Exception()


def get_fake_technical_metadata(file_path: Path) -> str:
    return FileMetaData(mimetype="image/jpeg", metadata=f"<xml>{file_path}</xml>", metadata_mimetype="text/xml+mix")


def process_basic_image(
    identifier: str,
    input_path: Path,
    output_path: Path,
    get_technical_metadata: Callable[[Path], str] = get_fake_technical_metadata
) -> bool:
    file_provider = FilesystemFileProvider()
    file_provider.create_directory(output_path / identifier)
    file_provider.create_directory(output_path / identifier / "data")
    file_provider.create_directory(output_path / identifier / "metadata")

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

    return True
