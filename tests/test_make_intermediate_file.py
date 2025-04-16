import tempfile
from pathlib import Path

import pytest

from dor.adapters.make_intermediate_file import make_intermediate_file
from dor.adapters.technical_metadata import ImageTechnicalMetadata, Mimetype


@pytest.fixture
def fixtures_path() -> Path:
    return Path("tests/fixtures/test_file_set_images")


def test_make_intermediate_file_converts_jpg_to_uncompressed_tiff(fixtures_path):
    image_path = fixtures_path / "test_image.jpg"
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=".tiff")
    with temp_file:
        temp_file_path = Path(temp_file.name)
        make_intermediate_file(image_path, temp_file_path)
        tech_metadata = ImageTechnicalMetadata.create(temp_file_path)

    assert tech_metadata.mimetype == Mimetype.TIFF
    assert not tech_metadata.compressed


def test_make_intermediate_file_unrotates_tiff(fixtures_path):
    image_path = fixtures_path / "test_image_rotated.tiff"
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=".tiff")
    with temp_file:
        temp_file_path = Path(temp_file.name)
        make_intermediate_file(image_path, temp_file_path)
        tech_metadata = ImageTechnicalMetadata.create(temp_file_path)

    assert tech_metadata.mimetype == Mimetype.TIFF
    assert not tech_metadata.rotated


def test_make_intermediate_file_uncompresses_tiff(fixtures_path):
    image_path = fixtures_path / "test_image_compressed.tiff"
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=".tiff")
    with temp_file:
        temp_file_path = Path(temp_file.name)
        make_intermediate_file(image_path, temp_file_path)
        tech_metadata = ImageTechnicalMetadata.create(temp_file_path)

    assert tech_metadata.mimetype == Mimetype.TIFF
    assert not tech_metadata.compressed
