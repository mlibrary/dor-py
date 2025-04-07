from pathlib import Path

import pytest

from dor.adapters.generate_service_variant import generate_service_variant
from dor.adapters.technical_metadata import ImageMimetype, get_technical_metadata


@pytest.fixture
def fixtures_path() -> Path:
    return Path("tests/fixtures/test_file_set_images")


def test_generate_service_variant_converts_to_jp2(fixtures_path):
    image_path = fixtures_path / "test_image.tiff"
    output_path = "tests/test_generate_service_variant_output/test_image.jp2"
    generate_service_variant(image_path, output_path)
    techmetadata = get_technical_metadata(output_path)
    
    assert techmetadata.mimetype == ImageMimetype.JP2

