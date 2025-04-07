from pathlib import Path

import pytest

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.process_basic_image import process_basic_image


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


def test_process_basic_copy_copies_input_file_to_output_file(input_path, output_path):
    identifier = "uuid"
    copy_of_source_file = output_path / identifier / "data" / ("test_image.function:source.format:image.jpg")

    assert process_basic_image(identifier, input_path / "test_image.jpg", output_path)
    assert copy_of_source_file.exists()


def test_process_basic_image_creates_technical_metadata(input_path, output_path):
    identifier = "uuid"
    technical_metadata_file = output_path / identifier / "metadata" / \
        ("test_image.function:source.format:image.jpg.function:technical.mix.xml")
    assert process_basic_image(identifier, input_path / "test_image.jpg", output_path)
    assert technical_metadata_file.exists()


def test_process_basic_image_creates_service_image(input_path, output_path):
    identifier = "uuid"
    service_image_file = output_path / identifier / "data" / \
        ("test_image.function:service.format:image.jp2")
    assert process_basic_image(identifier, input_path / "test_image.jpg", output_path)
    assert service_image_file.exists()


def test_process_basic_image_creates_service_technical_metadata(input_path, output_path):
    identifier = "uuid"
    technical_metadata_file = output_path / identifier / "metadata" / \
        ("test_image.function:service.format:image.jp2.function:technical.mix.xml")
    assert process_basic_image(identifier, input_path / "test_image.jpg", output_path)
    assert technical_metadata_file.exists()


def test_process_basic_image_creates_descriptor_file(input_path, output_path):
    identifier = "uuid"
    descriptor_file = output_path / identifier / "descriptor" / \
        (f"{identifier}.file_set.mets2.xml")
    assert process_basic_image(identifier, input_path / "test_image.jpg", output_path)
    assert descriptor_file.exists()

