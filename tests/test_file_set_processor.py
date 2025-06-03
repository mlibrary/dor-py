from pathlib import Path

import pytest

from dor.providers.file_set_identifier import FileSetIdentifier
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.operations import CompressSourceImage
from dor.providers.build_file_set import (
    Command,
    Input,
    build_file_set,
)


@pytest.fixture
def file_set_identifier() -> FileSetIdentifier:
    return FileSetIdentifier(project_id="collid", file_name="test_image.jpg")


@pytest.fixture
def input_path() -> Path:
    return Path("tests/fixtures/test_file_set_processor")


@pytest.fixture
def output_path() -> Path:
    file_provider = FilesystemFileProvider()
    output_path = Path("tests/output/test_file_set_processor")
    file_provider.delete_dir_and_contents(output_path)
    file_provider.create_directory(output_path)
    return output_path


@pytest.fixture
def image_input(input_path: Path) -> Input:
    commands = [Command(operation=CompressSourceImage, kwargs={})]
    return Input(file_path=input_path / "test_image.jpg", commands=commands)


def test_process_basic_image_copy_copies_input_file_to_output_file(file_set_identifier, image_input, output_path):
    copy_of_source_file = output_path / file_set_identifier.identifier /  \
        "data" / ("test_image.function:source.format:image.jpg")

    assert build_file_set(
        file_set_identifier=file_set_identifier,
        inputs=[image_input],
        output_path=output_path
    )
    assert copy_of_source_file.exists()


def test_process_basic_image_creates_technical_metadata(file_set_identifier, image_input, output_path):
    technical_metadata_file = output_path / file_set_identifier.identifier / "metadata" / \
        ("test_image.function:source.format:image.jpg.function:technical.mix.xml")
    assert build_file_set(
        file_set_identifier=file_set_identifier,
        inputs=[image_input],
        output_path=output_path
    )
    assert technical_metadata_file.exists()


def test_process_basic_image_creates_service_image(file_set_identifier, image_input, output_path):
    service_image_file = output_path / file_set_identifier.identifier / "data" / \
        ("test_image.function:service.format:image.jp2")
    assert build_file_set(
        file_set_identifier=file_set_identifier,
        inputs=[image_input],
        output_path=output_path
    )
    assert service_image_file.exists()


def test_process_basic_image_creates_service_technical_metadata(file_set_identifier, image_input, output_path):
    technical_metadata_file = output_path / file_set_identifier.identifier / "metadata" / \
        ("test_image.function:service.format:image.jp2.function:technical.mix.xml")
    assert build_file_set(
        file_set_identifier=file_set_identifier,
        inputs=[image_input],
        output_path=output_path
    )
    assert technical_metadata_file.exists()


def test_process_basic_image_creates_descriptor_file(file_set_identifier, image_input, output_path):
    descriptor_file = output_path / file_set_identifier.identifier / "descriptor" / \
        (f"{file_set_identifier.uuid}.file_set.mets2.xml")
    assert build_file_set(
        file_set_identifier=file_set_identifier,
        inputs=[image_input],
        output_path=output_path
    )
    assert descriptor_file.exists()


def test_process_basic_image_creates_service_event_metadata(file_set_identifier, image_input, output_path):
    event_metadata_file = output_path / file_set_identifier.identifier / "metadata" / \
        ("test_image.function:service.format:image.jp2.function:event.premis.xml")
    assert build_file_set(
        file_set_identifier=file_set_identifier,
        inputs=[image_input],
        output_path=output_path
    )
    assert event_metadata_file.exists()


def test_process_basic_image_creates_source_event_metadata(file_set_identifier, image_input, output_path):
    event_metadata_file = output_path / file_set_identifier.identifier / "metadata" / \
        ("test_image.function:source.format:image.jpg.function:event.premis.xml")
    assert build_file_set(
        file_set_identifier=file_set_identifier,
        inputs=[image_input],
        output_path=output_path
    )
    assert event_metadata_file.exists()
