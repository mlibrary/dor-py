import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from dor.adapters.image_reader import AltoDoc, TesseractImageReader, TesseractImageReaderError


@pytest.fixture
def quick_brown() -> Path:
    return Path("tests/fixtures/test_image_reader/quick-brown.tiff")


def test_tesseract_image_reader_fails_when_unknown_language_is_specified():
    with pytest.raises(TesseractImageReaderError):
        TesseractImageReader.create(Path("some/path"), language="xyz")


def test_tesseract_image_reader_can_read_simple_document(quick_brown):
    expected_text = "The quick\nbrown fox\njumps over the\nlazy dog."
    text = TesseractImageReader.create(quick_brown).text
    assert expected_text == text.strip()


def test_tesseract_image_reader_can_create_alto_xml_for_simple_document(quick_brown):
    alto_xml = TesseractImageReader.create(quick_brown).alto
    assert alto_xml is not None
    alto = ET.fromstring(alto_xml)
    assert alto is not None


def test_alto_doc_can_return_annotation_data_for_simple_document(quick_brown):
    data = AltoDoc(TesseractImageReader.create(quick_brown).alto).annotation_data

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

    assert data == expected_data
