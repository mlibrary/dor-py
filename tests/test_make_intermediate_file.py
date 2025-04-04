import tempfile
from pathlib import Path

import pytest

from dor.adapters.make_intermediate_file import make_intermediate_file
from dor.adapters.technical_metadata import ImageMimetype, get_technical_metadata


@pytest.fixture
def fixtures_path() -> Path:
    return Path("tests/fixtures/test_technical_metadata")


def test_make_intermediate_file_converts_jpg_to_uncompressed_tiff(fixtures_path):
    image_path = fixtures_path / "test_image.jpg"
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=".tiff")
    with temp_file:
        temp_file_path = Path(temp_file.name)
        make_intermediate_file(image_path, temp_file_path)
        tech_metadata = get_technical_metadata(temp_file_path)

    assert tech_metadata.mimetype == ImageMimetype.TIFF
    assert not tech_metadata.compressed


def test_make_intermediate_file_unrotates_tiff(fixtures_path):
    image_path = fixtures_path / "test_image_rotated.tiff"
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=".tiff")
    with temp_file:
        temp_file_path = Path(temp_file.name)
        make_intermediate_file(image_path, temp_file_path)
        tech_metadata = get_technical_metadata(temp_file_path)

    assert tech_metadata.mimetype == ImageMimetype.TIFF
    assert not tech_metadata.rotated
