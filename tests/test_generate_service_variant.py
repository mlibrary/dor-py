from pathlib import Path

import pytest

from dor.adapters.generate_service_variant import generate_service_variant
from dor.adapters.technical_metadata import ImageMimetype, ImageTechnicalMetadata
from dor.providers.file_system_file_provider import FilesystemFileProvider


@pytest.fixture
def fixtures_path() -> Path:
    return Path("tests/fixtures/test_file_set_images")


@pytest.fixture
def output_path() -> Path:
    file_provider = FilesystemFileProvider()
    output_path = Path("tests/test_generate_service_variant_output")
    file_provider.delete_dir_and_contents(output_path)
    file_provider.create_directory(output_path)
    return output_path


def test_generate_service_variant_converts_to_jp2(fixtures_path, output_path):
    image_path = fixtures_path / "test_image.tiff"
    output_path = output_path / "test_image.jp2"
    generate_service_variant(image_path, output_path)
    techmetadata = ImageTechnicalMetadata.create(output_path)
    
    assert techmetadata.mimetype == ImageMimetype.JP2

