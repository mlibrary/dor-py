import shutil
from pathlib import Path
from typing import Callable

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.builders.parts import FileInfo, UseFunction, UseFormat


class TechnicalMetadataError(Exception):
    pass


def get_source_file_path(input_path: Path) -> Path:
    for file_path in input_path.iterdir():
        return file_path
    raise Exception()


def get_fake_technical_metadata(file_path: Path) -> str:
    return f"<xml>{file_path}</xml>"


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

    image_file_info = FileInfo(
        identifier, basename, [UseFunction.source, UseFormat.image], "image/jpeg"
    )
    new_source_file_path = output_path / identifier / image_file_info.path

    shutil.copyfile(source_file_path, new_source_file_path)

    try:
        tech_xml_data = get_technical_metadata(new_source_file_path)
    except TechnicalMetadataError as error:
        return False

    tech_meta_file_info = image_file_info.metadata(UseFunction.technical, "text/xml+mix")
    (output_path / identifier / tech_meta_file_info.path).write_text(tech_xml_data)

    return True
