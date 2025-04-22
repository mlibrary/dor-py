import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from dor.adapters.image_text_extractor import (
    AltoDoc, AnnotationData, ImageTextExtractor, ImageTextExtractorError
)


@pytest.fixture
def quick_brown() -> Path:
    return Path("tests/fixtures/test_image_reader/quick-brown.tiff")


def test_image_text_extractor_fails_when_unknown_language_is_specified():
    with pytest.raises(ImageTextExtractorError):
        ImageTextExtractor.create(Path("some/path"), language="xyz")


def test_image_text_extractor_can_read_simple_document(quick_brown):
    expected_text = "The quick\nbrown fox\njumps over the\nlazy dog."
    text = ImageTextExtractor.create(quick_brown).text
    assert expected_text == text.strip()


def test_image_text_extractor_can_create_alto_xml_for_simple_document(quick_brown):
    alto_xml = ImageTextExtractor.create(quick_brown).alto
    assert alto_xml is not None
    alto = ET.fromstring(alto_xml)
    assert alto is not None


def test_annotation_data_can_return_data_for_simple_document(quick_brown):
    image_reader = ImageTextExtractor.create(quick_brown)
    annotation_data = AnnotationData(AltoDoc.create(image_reader.alto))

    expected_data = {
        "page": {"width": 1700, "height": 2200},
        "words": {
            "the": [[207, 240, 509, 384], [1157, 707, 1399, 851]],
            "quick": [[573, 240, 1018, 424]],
            "brown": [[201, 473, 717, 617]],
            "fox": [[776, 473, 1037, 617]],
            "jumps": [[184, 707, 689, 891]],
            "over": [[753, 755, 1107, 851]],
            "lazy": [[206, 940, 536, 1124]],
            "dog": [[595, 940, 930, 1124]]
        }
    }

    assert annotation_data.data == expected_data
