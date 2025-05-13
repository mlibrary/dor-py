from pathlib import Path

import pytest

from dor.adapters.technical_metadata import ImageTechnicalMetadata
from dor.providers.file_set_identifier import FileSetIdentifier
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.operations import CompressSourceImage
from dor.providers.process_basic_image import (
    Command,
    Input,
    build_file_set,
)


@pytest.fixture
def file_set_identifier() -> FileSetIdentifier:
    return FileSetIdentifier(project_id="collid", file_name="test_image_rotated.tiff")


@pytest.fixture
def input_path() -> Path:
    return Path("tests/fixtures/test_basic_copy_needing_rotation")


@pytest.fixture
def output_path() -> Path:
    file_provider = FilesystemFileProvider()
    output_path = Path("tests/test_basic_copy_needing_rotation")
    file_provider.delete_dir_and_contents(output_path)
    file_provider.create_directory(output_path)
    return output_path


@pytest.fixture
def image_input(input_path: Path) -> Input:
    commands = [Command(operation=CompressSourceImage, kwargs={})]
    return Input(file_path=input_path / "test_image_rotated.tiff", commands=commands)


def test_process_basic_image_creates_service_image(file_set_identifier, image_input, output_path):
    service_image_file = output_path / file_set_identifier.identifier / "data" / \
        ("test_image_rotated.function:service.format:image.jp2")
    assert build_file_set(
        file_set_identifier=file_set_identifier,
        inputs=[image_input],
        output_path=output_path
    )
    assert service_image_file.exists()

    tech_metadata = ImageTechnicalMetadata.create(service_image_file)
    assert tech_metadata.rotated is False
