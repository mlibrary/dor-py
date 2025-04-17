from pathlib import Path

import pytest

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.process_basic_image import FileSetIdentifier, process_basic_image


@pytest.fixture
def file_set_identifier() -> FileSetIdentifier:
    return FileSetIdentifier(project_id="collid", file_name="test_image.jpg")


@pytest.fixture
def input_path() -> Path:
    return Path("tests/fixtures/test_basic_copy")


@pytest.fixture
def output_path() -> Path:
    file_provider = FilesystemFileProvider()
    output_path = Path("tests/test_process_basic_image_output")
    file_provider.delete_dir_and_contents(output_path)
    file_provider.create_directory(output_path)
    return output_path


def test_process_basic_image_copy_copies_input_file_to_output_file(file_set_identifier, input_path, output_path):
    copy_of_source_file = output_path / file_set_identifier.identifier / \
        "data" / ("test_image.function:source.format:image.jpg")

    assert process_basic_image(
        file_set_identifier=file_set_identifier,
        image_path=input_path / "test_image.jpg",
        output_path=output_path
    )
    assert copy_of_source_file.exists()


def test_process_basic_image_creates_technical_metadata(file_set_identifier, input_path, output_path):
    technical_metadata_file = output_path / file_set_identifier.identifier / "metadata" / \
        ("test_image.function:source.format:image.jpg.function:technical.mix.xml")
    assert process_basic_image(
        file_set_identifier=file_set_identifier,
        image_path=input_path / "test_image.jpg",
        output_path=output_path
    )
    assert technical_metadata_file.exists()


def test_process_basic_image_creates_service_image(file_set_identifier, input_path, output_path):
    service_image_file = output_path / file_set_identifier.identifier / "data" / \
        ("test_image.function:service.format:image.jp2")
    assert process_basic_image(
        file_set_identifier=file_set_identifier,
        image_path=input_path / "test_image.jpg",
        output_path=output_path
    )
    assert service_image_file.exists()


def test_process_basic_image_creates_service_technical_metadata(file_set_identifier, input_path, output_path):
    technical_metadata_file = output_path / file_set_identifier.identifier / "metadata" / \
        ("test_image.function:service.format:image.jp2.function:technical.mix.xml")
    assert process_basic_image(
        file_set_identifier=file_set_identifier,
        image_path=input_path / "test_image.jpg",
        output_path=output_path
    )
    assert technical_metadata_file.exists()


def test_process_basic_image_creates_descriptor_file(file_set_identifier, input_path, output_path):
    descriptor_file = output_path / file_set_identifier.identifier / "descriptor" / \
        (f"{file_set_identifier.uuid}.file_set.mets2.xml")
    assert process_basic_image(
        file_set_identifier=file_set_identifier,
        image_path=input_path / "test_image.jpg",
        output_path=output_path
    )
    assert descriptor_file.exists()


def test_process_basic_image_creates_service_event_metadata(file_set_identifier, input_path, output_path):
    event_metadata_file = output_path / file_set_identifier.identifier / "metadata" / \
        ("test_image.function:service.format:image.jp2.function:event.premis.xml")
    assert process_basic_image(
        file_set_identifier=file_set_identifier,
        image_path=input_path / "test_image.jpg",
        output_path=output_path
    )
    assert event_metadata_file.exists()


def test_process_basic_image_creates_source_event_metadata(file_set_identifier, input_path, output_path):
    event_metadata_file = output_path / file_set_identifier.identifier / "metadata" / \
        ("test_image.function:source.format:image.jpg.function:event.premis.xml")
    assert process_basic_image(
        file_set_identifier=file_set_identifier,
        image_path=input_path / "test_image.jpg",
        output_path=output_path
    )
    assert event_metadata_file.exists()
