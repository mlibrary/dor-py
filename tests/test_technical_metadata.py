from pathlib import Path

import pytest

from dor.adapters.technical_metadata import get_technical_metadata


@pytest.fixture
def fixtures_path() -> Path:
    return Path("tests/fixtures/test_technical_metadata")


def test_get_technical_metadata_for_valid_jpg(fixtures_path: Path):
    image_path = fixtures_path / "test_image.jpg"
    tech_metadata = get_technical_metadata(image_path)
    assert tech_metadata.mimetype == "image/jpeg"
    assert tech_metadata.metadata_mimetype == "text/xml+mix"
    assert not tech_metadata.rotated
    assert tech_metadata.compressed
    assert tech_metadata.metadata


def test_get_technical_metadata_for_valid_tiff(fixtures_path: Path):
    image_path = fixtures_path / "test_image.tiff"
    tech_metadata = get_technical_metadata(image_path)
    assert tech_metadata.mimetype == "image/tiff"
    assert tech_metadata.metadata_mimetype == "text/xml+mix"
    assert not tech_metadata.rotated
    assert not tech_metadata.compressed
    assert tech_metadata.metadata
