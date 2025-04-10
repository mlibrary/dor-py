from pathlib import Path

import pytest

from dor.adapters.technical_metadata import ImageMimetype, TechnicalMetadataMimetype, get_technical_metadata


@pytest.fixture
def fixtures_path() -> Path:
    return Path("tests/fixtures/test_file_set_images")


def test_get_technical_metadata_retrieves_data_for_jpg(fixtures_path: Path):
    image_path = fixtures_path / "test_image.jpg"
    tech_metadata = get_technical_metadata(image_path)
    assert tech_metadata.mimetype == ImageMimetype.JPEG
    assert tech_metadata.metadata_mimetype == TechnicalMetadataMimetype.MIX
    assert not tech_metadata.rotated
    assert tech_metadata.compressed
    assert tech_metadata.metadata


def test_get_technical_metadata_retrieves_data_for_tiff(fixtures_path: Path):
    image_path = fixtures_path / "test_image.tiff"
    tech_metadata = get_technical_metadata(image_path)
    assert tech_metadata.mimetype == ImageMimetype.TIFF
    assert tech_metadata.metadata_mimetype == TechnicalMetadataMimetype.MIX
    assert not tech_metadata.rotated
    assert not tech_metadata.compressed
    assert tech_metadata.metadata


def test_get_technical_metadata_retrieves_data_for_rotated_tiff(fixtures_path: Path):
    image_path = fixtures_path / "test_image_rotated.tiff"
    tech_metadata = get_technical_metadata(image_path)
    assert tech_metadata.mimetype == ImageMimetype.TIFF
    assert tech_metadata.metadata_mimetype == TechnicalMetadataMimetype.MIX
    assert tech_metadata.rotated
    assert not tech_metadata.compressed
    assert tech_metadata.metadata
