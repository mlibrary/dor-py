from pathlib import Path

import pytest

from dor.adapters.image_reader import TesseractImageReader, TesseractImageReaderError


@pytest.fixture
def quick_brown() -> Path:
    return Path("tests/fixtures/test_image_reader/quick-brown.tiff")


def test_tesseract_image_reader_fails_when_unknown_language_is_specified():
    with pytest.raises(TesseractImageReaderError):
        TesseractImageReader(Path("some/path"), language="xyz")


def test_tesseract_image_reader_can_read_simple_document(quick_brown):
    expected_text = "The quick\nbrown fox\njumped over\nthe lazy dog."
    text = TesseractImageReader(quick_brown).text
    assert expected_text == text.strip()
