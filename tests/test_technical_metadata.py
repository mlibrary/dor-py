from pathlib import Path

import pytest

from dor.adapters.technical_metadata import get_technical_metadata


@pytest.fixture
def image_path() -> Path:
    return Path("tests/fixtures/test_basic_copy/test_image.jpg")


def test_get_technical_metadata_for_valid_image(image_path):
    tech_metadata = get_technical_metadata(image_path)
    assert tech_metadata.mimetype == "image/jpeg"
    assert tech_metadata.metadata_mimetype == "text/xml+mix"
    assert not tech_metadata.rotated
    assert tech_metadata.compressed
    assert tech_metadata.metadata
