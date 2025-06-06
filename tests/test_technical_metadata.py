import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from dor.adapters.technical_metadata import (
    ImageTechnicalMetadata, JHOVEDoc, JHOVEDocError, Mimetype, NS_MAP,
    TechnicalMetadataMimetype, TextTechnicalMetadata
)


@pytest.fixture
def file_set_images_path() -> Path:
    return Path("tests/fixtures/test_file_set_images")


@pytest.fixture
def fixtures_path() -> Path:
    return Path("tests/fixtures/test_technical_metadata")


@pytest.fixture
def jhove_elem(fixtures_path: Path) -> ET.Element:
    doc_path = fixtures_path / "jhove_output.xml"
    return ET.fromstring(doc_path.read_text())


def test_image_tech_metadata_retrieves_data_for_jpg(file_set_images_path: Path):
    image_path = file_set_images_path / "test_image.jpg"
    tech_metadata = ImageTechnicalMetadata.create(image_path)
    assert tech_metadata.mimetype == Mimetype.JPEG
    assert tech_metadata.metadata_mimetype == TechnicalMetadataMimetype.MIX
    assert not tech_metadata.rotated
    assert tech_metadata.compressed
    assert tech_metadata.metadata is not None


def test_image_tech_metadata_retrieves_data_for_tiff(file_set_images_path: Path):
    image_path = file_set_images_path / "test_image.tiff"
    tech_metadata = ImageTechnicalMetadata.create(image_path)
    assert tech_metadata.mimetype == Mimetype.TIFF
    assert tech_metadata.metadata_mimetype == TechnicalMetadataMimetype.MIX
    assert not tech_metadata.rotated
    assert not tech_metadata.compressed
    assert tech_metadata.metadata is not None


def test_image_tech_metadata_retrieves_data_for_rotated_tiff(file_set_images_path: Path):
    image_path = file_set_images_path / "test_image_rotated.tiff"
    tech_metadata = ImageTechnicalMetadata.create(image_path)
    assert tech_metadata.mimetype == Mimetype.TIFF
    assert tech_metadata.metadata_mimetype == TechnicalMetadataMimetype.MIX
    assert tech_metadata.rotated
    assert not tech_metadata.compressed
    assert tech_metadata.metadata is not None


def test_text_tech_metadata_retrieves_data_for_ascii_text(fixtures_path: Path):
    text_path = fixtures_path / "sample_ascii.txt"
    tech_metadata = TextTechnicalMetadata.create(text_path)
    assert tech_metadata.mimetype == Mimetype.TXT_ASCII
    assert tech_metadata.metadata_mimetype == TechnicalMetadataMimetype.TEXTMD
    assert tech_metadata.metadata is not None


def test_text_tech_metadata_retrieves_data_for_utf_text(fixtures_path: Path):
    text_path = fixtures_path / "sample_utf8.txt"
    tech_metadata = TextTechnicalMetadata.create(text_path)
    assert tech_metadata.mimetype == Mimetype.TXT_UTF8
    assert tech_metadata.metadata_mimetype == TechnicalMetadataMimetype.TEXTMD
    assert tech_metadata.metadata is not None


def test_jhove_doc_fails_when_status_is_invalid(jhove_elem: ET.Element):
    status_elem = jhove_elem.find(".//jhove:repInfo/jhove:status", NS_MAP)
    if status_elem is None: raise Exception
    status_elem.text = "Unknown"

    with pytest.raises(JHOVEDocError):
        JHOVEDoc(jhove_elem, "Dummy").technical_metadata


def test_jhove_doc_fails_when_encountering_unknown_mimetype(jhove_elem: ET.Element):
    mimetype_elem = jhove_elem.find(".//jhove:repInfo/jhove:mimeType", NS_MAP)
    if mimetype_elem is None: raise Exception
    mimetype_elem.text = "image/png"

    with pytest.raises(JHOVEDocError):
        JHOVEDoc(jhove_elem, "Dummy").technical_metadata


def test_jhove_doc_fails_when_status_is_missing(jhove_elem: ET.Element):
    rep_info_elem = jhove_elem.find(".//jhove:repInfo", NS_MAP)
    if rep_info_elem is None: raise Exception
    status_elem = rep_info_elem.find("./jhove:status", NS_MAP)
    if status_elem is None: raise Exception
    rep_info_elem.remove(status_elem)

    with pytest.raises(JHOVEDocError):
        JHOVEDoc(jhove_elem, "Dummy").status


def test_jhove_doc_fails_when_status_has_no_text(jhove_elem: ET.Element):
    status_elem = jhove_elem.find(".//jhove:repInfo/jhove:status", NS_MAP)
    if status_elem is None: raise Exception
    status_elem.text = None

    with pytest.raises(JHOVEDocError):
        JHOVEDoc(jhove_elem, "Dummy").status


def test_jhove_doc_fails_when_mimetype_is_missing(jhove_elem: ET.Element):
    rep_info_elem = jhove_elem.find(".//jhove:repInfo", NS_MAP)
    if rep_info_elem is None: raise Exception
    mimetype_elem = rep_info_elem.find("./jhove:mimeType", NS_MAP)
    if mimetype_elem is None: raise Exception
    rep_info_elem.remove(mimetype_elem)

    with pytest.raises(JHOVEDocError):
        JHOVEDoc(jhove_elem, "Dummy").mimetype


def test_jhove_doc_fails_when_mimetype_has_no_text(jhove_elem: ET.Element):
    mimetype_elem = jhove_elem.find(".//jhove:repInfo/jhove:mimeType", NS_MAP)
    if mimetype_elem is None: raise Exception
    mimetype_elem.text = None

    with pytest.raises(JHOVEDocError):
        JHOVEDoc(jhove_elem, "Dummy").mimetype


def test_jhove_doc_fails_when_mix_is_missing(jhove_elem: ET.Element):
    niso_value_elem = jhove_elem.find(
        f".//jhove:values[@type='NISOImageMetadata']/jhove:value", NS_MAP
    )
    if niso_value_elem is None: raise Exception
    niso_mix_elem = niso_value_elem.find("./mix:mix", NS_MAP)
    if niso_mix_elem is None: raise Exception
    niso_value_elem.remove(niso_mix_elem)

    with pytest.raises(JHOVEDocError):
        JHOVEDoc(jhove_elem, "NISOImageMetadata").technical_metadata
