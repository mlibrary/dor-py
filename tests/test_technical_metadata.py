import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from dor.adapters.technical_metadata import (
    ImageMimetype, JHOVEParser, JHOVEParserError, NS_MAP, TechnicalMetadataError,
    TechnicalMetadataGatherer, TechnicalMetadataMimetype
)


@pytest.fixture
def fixtures_path() -> Path:
    return Path("tests/fixtures/test_file_set_images")


@pytest.fixture
def jhove_doc() -> ET.Element:
    doc_path = Path("tests/fixtures/test_technical_metadata/jhove_output.xml")
    return ET.fromstring(doc_path.read_text())


def test_gatherer_retrieves_data_for_jpg(fixtures_path: Path):
    image_path = fixtures_path / "test_image.jpg"
    tech_metadata = TechnicalMetadataGatherer(image_path).gather()
    assert tech_metadata.mimetype == ImageMimetype.JPEG
    assert tech_metadata.metadata_mimetype == TechnicalMetadataMimetype.MIX
    assert not tech_metadata.rotated
    assert tech_metadata.compressed
    assert tech_metadata.metadata


def test_gatherer_retrieves_data_for_tiff(fixtures_path: Path):
    image_path = fixtures_path / "test_image.tiff"
    tech_metadata = TechnicalMetadataGatherer(image_path).gather()
    assert tech_metadata.mimetype == ImageMimetype.TIFF
    assert tech_metadata.metadata_mimetype == TechnicalMetadataMimetype.MIX
    assert not tech_metadata.rotated
    assert not tech_metadata.compressed
    assert tech_metadata.metadata


def test_gatherer_retrieves_data_for_rotated_tiff(fixtures_path: Path):
    image_path = fixtures_path / "test_image_rotated.tiff"
    tech_metadata = TechnicalMetadataGatherer(image_path).gather()
    assert tech_metadata.mimetype == ImageMimetype.TIFF
    assert tech_metadata.metadata_mimetype == TechnicalMetadataMimetype.MIX
    assert tech_metadata.rotated
    assert not tech_metadata.compressed
    assert tech_metadata.metadata


def test_create_metadata_fails_when_encountering_unknown_mimetype(jhove_doc: ET.Element):
    mimetype_elem = jhove_doc.find(".//jhove:repInfo/jhove:mimeType", NS_MAP)
    if mimetype_elem is None: raise Exception
    mimetype_elem.text = "image/png"

    with pytest.raises(TechnicalMetadataError):
        gatherer = TechnicalMetadataGatherer(Path("some/path"))
        gatherer.create_metadata(jhove_doc)


def test_create_metadata_fails_when_status_is_invalid(jhove_doc: ET.Element):
    status_elem = jhove_doc.find(".//jhove:repInfo/jhove:status", NS_MAP)
    if status_elem is None: raise Exception
    status_elem.text = "Unknown"

    with pytest.raises(TechnicalMetadataError):
        gatherer = TechnicalMetadataGatherer(Path("some/path"))
        gatherer.create_metadata(jhove_doc)


def test_jhove_parser_fails_when_status_is_missing(jhove_doc: ET.Element):
    rep_info_elem = jhove_doc.find(".//jhove:repInfo", NS_MAP)
    if rep_info_elem is None: raise Exception
    status_elem = rep_info_elem.find("./jhove:status", NS_MAP)
    if status_elem is None: raise Exception
    rep_info_elem.remove(status_elem)

    with pytest.raises(JHOVEParserError):
        JHOVEParser(jhove_doc).get_status()


def test_jhove_parser_fails_when_status_has_no_text(jhove_doc: ET.Element):
    status_elem = jhove_doc.find(".//jhove:repInfo/jhove:status", NS_MAP)
    if status_elem is None: raise Exception
    status_elem.text = None

    with pytest.raises(JHOVEParserError):
        JHOVEParser(jhove_doc).get_status()


def test_jhove_parser_fails_when_mimetype_is_missing(jhove_doc: ET.Element):
    rep_info_elem = jhove_doc.find(".//jhove:repInfo", NS_MAP)
    if rep_info_elem is None: raise Exception
    mimetype_elem = rep_info_elem.find("./jhove:mimeType", NS_MAP)
    if mimetype_elem is None: raise Exception
    rep_info_elem.remove(mimetype_elem)

    with pytest.raises(JHOVEParserError):
        JHOVEParser(jhove_doc).get_mimetype()


def test_jhove_parser_fails_when_mimetype_has_no_text(jhove_doc: ET.Element):
    mimetype_elem = jhove_doc.find(".//jhove:repInfo/jhove:mimeType", NS_MAP)
    if mimetype_elem is None: raise Exception
    mimetype_elem.text = None

    with pytest.raises(JHOVEParserError):
        JHOVEParser(jhove_doc).get_mimetype()


def test_jhove_parser_fails_when_mix_is_missing(jhove_doc: ET.Element):
    niso_value_elem = jhove_doc.find(
        f".//jhove:values[@type='NISOImageMetadata']/jhove:value", NS_MAP
    )
    if niso_value_elem is None: raise Exception
    niso_mix_elem = niso_value_elem.find("./mix:mix", NS_MAP)
    if niso_mix_elem is None: raise Exception
    niso_value_elem.remove(niso_mix_elem)

    with pytest.raises(JHOVEParserError):
        JHOVEParser(jhove_doc).get_niso_mix()


def test_jhove_parser_fails_when_compression_is_missing(jhove_doc: ET.Element):
    compression_elem = jhove_doc.find(".//mix:Compression", NS_MAP)
    if compression_elem is None: raise Exception
    compression_scheme_elem = compression_elem.find("./mix:compressionScheme", NS_MAP)
    if compression_scheme_elem is None: raise Exception
    compression_elem.remove(compression_scheme_elem)

    with pytest.raises(JHOVEParserError):
        JHOVEParser(jhove_doc).get_compressed()


def test_jhove_parser_fails_when_compression_has_no_text(jhove_doc: ET.Element):
    compression_scheme_elem = jhove_doc.find(".//mix:Compression/mix:compressionScheme", NS_MAP)
    if compression_scheme_elem is None: raise Exception
    compression_scheme_elem.text = None

    with pytest.raises(JHOVEParserError):
        JHOVEParser(jhove_doc).get_compressed()
