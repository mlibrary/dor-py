from pathlib import Path

import pytest

from dor.providers.file_set_identifier import FileSetIdentifier
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.operations import (
    CompressSourceImage,
    CreateTextAnnotationData,
    ExtractImageText,
    ExtractImageTextCoordinates,
)
from dor.providers.build_file_set import (
    Command,
    Input,
    build_file_set,
)


@pytest.fixture
def file_set_identifier() -> FileSetIdentifier:
    return FileSetIdentifier(project_id="collid", file_name="quick-brown.jp2")


@pytest.fixture
def input_path() -> Path:
    return Path("tests/fixtures/test_basic_copy_jp2_with_ocr")


@pytest.fixture
def output_path() -> Path:
    file_provider = FilesystemFileProvider()
    output_path = Path("tests/test_process_image_jp2_with_ocr")
    file_provider.delete_dir_and_contents(output_path)
    file_provider.create_directory(output_path)
    return output_path


@pytest.fixture
def jp2_image_with_ocr_input(input_path: Path) -> Input:
    commands = [
        Command(operation=CompressSourceImage, kwargs={}),
        Command(operation=ExtractImageTextCoordinates, kwargs={}),
        Command(operation=ExtractImageText, kwargs={}),
        Command(operation=CreateTextAnnotationData, kwargs={}),
    ]
    return Input(file_path=input_path / "quick-brown.jp2", commands=commands)


def test_process_creates_source_service_image_for_jp2(
    file_set_identifier, jp2_image_with_ocr_input, output_path
):
    assert build_file_set(
        file_set_identifier=file_set_identifier,
        inputs=[jp2_image_with_ocr_input],
        output_path=output_path
    )
  
    image_file = output_path / file_set_identifier.identifier /  \
        "data" / ("quick-brown.function:source.function:service.format:image.jp2")
    assert image_file.exists()


def test_process_creates_ocr_data_files(
    file_set_identifier, jp2_image_with_ocr_input, output_path
):
    assert build_file_set(
        file_set_identifier=file_set_identifier,
        inputs=[jp2_image_with_ocr_input],
        output_path=output_path
    )

    text_coordinates_file = output_path / file_set_identifier.identifier /  \
        "data" / ("quick-brown.function:service.format:text-coordinate.xml")
    text_coordinates_file.exists()

    plain_text_file = output_path / file_set_identifier.identifier /  \
        "data" / ("quick-brown.function:service.format:text-plain.txt")
    plain_text_file.exists()

    annotation_file = output_path / file_set_identifier.identifier /  \
        "data" / ("quick-brown.function:service.format:text-annotation.json")
    annotation_file.exists()
