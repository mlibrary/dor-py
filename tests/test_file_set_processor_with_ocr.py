from pathlib import Path

import pytest

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.process_basic_image import (
    Command,
    CompressSourceImage,
    ExtractImageText,
    FileSetIdentifier,
    Input,
    process_basic_image,
)

@pytest.fixture
def file_set_identifier() -> FileSetIdentifier:
    return FileSetIdentifier(project_id="collid", file_name="quick-brown.tiff")


@pytest.fixture
def input_path() -> Path:
    # Update this later
    return Path("tests/fixtures/test_image_text_extractor")


@pytest.fixture
def output_path() -> Path:
    file_provider = FilesystemFileProvider()
    output_path = Path("tests/test_process_image_with_ocr")
    file_provider.delete_dir_and_contents(output_path)
    file_provider.create_directory(output_path)
    return output_path


@pytest.fixture
def image_with_ocr_input(input_path: Path) -> Input:
    commands = [
        Command(operation=CompressSourceImage, kwargs={}),
        Command(operation=ExtractImageText, kwargs={})
    ]
    return Input(file_path=input_path / "quick-brown.tiff", commands=commands)


def test_process_creates_plain_text_file(file_set_identifier, image_with_ocr_input, output_path):
    copy_of_source_file = output_path / file_set_identifier.identifier /  \
        "data" / ("quick-brown.function:service.format:text-plain.txt")

    assert process_basic_image(
        file_set_identifier=file_set_identifier,
        inputs=[image_with_ocr_input],
        output_path=output_path
    )
    assert copy_of_source_file.exists()


def test_process_creates_technical_metadata_for_plain_text(file_set_identifier, image_with_ocr_input, output_path):
    technical_metadata_file = output_path / file_set_identifier.identifier / "metadata" / \
        ("quick-brown.function:service.format:text-plain.txt.function:technical.textmd.xml")
    assert process_basic_image(
        file_set_identifier=file_set_identifier,
        inputs=[image_with_ocr_input],
        output_path=output_path
    )
    assert technical_metadata_file.exists()


def test_process_creates_event_for_plain_text(file_set_identifier, image_with_ocr_input, output_path):
    event_metadata_file = output_path / file_set_identifier.identifier / "metadata" / \
        ("quick-brown.function:service.format:text-plain.txt.function:event.premis.xml")
    assert process_basic_image(
        file_set_identifier=file_set_identifier,
        inputs=[image_with_ocr_input],
        output_path=output_path
    )
    assert event_metadata_file.exists()
