import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

JHOVE_NS = "http://schema.openpreservation.org/ois/xml/ns/jhove"
MIX_NS = "http://www.loc.gov/mix/v20"
NS_MAP = {'jhove': JHOVE_NS, 'mix': MIX_NS}

JHOVE_VALID_OK = "Well-Formed and valid"
UNCOMPRESSED = "Uncompressed"
ROTATED = "rotated"

for prefix in NS_MAP:
    ET.register_namespace(prefix, NS_MAP[prefix])


class TechnicalMetadataError(Exception):
    pass


class ImageMimetype(Enum):
    JPEG = "image/jpeg"
    TIFF = "image/tiff"
    JP2 = "image/jp2"


class TechnicalMetadataMimetype(Enum):
    MIX = "text/xml+mix"


@dataclass
class TechnicalMetadata:
    mimetype: ImageMimetype
    metadata: str
    metadata_mimetype: TechnicalMetadataMimetype
    rotated: bool = False
    compressed: bool = False


def retrieve_element(jhove_doc: ET.Element, path: str) -> ET.Element:
    elem = jhove_doc.find(path, NS_MAP)
    if elem is None:
        raise TechnicalMetadataError(f"No element found at path {path}")
    return elem


def retrieve_element_text(jhove_doc: ET.Element, path: str) -> str:
    elem = retrieve_element(jhove_doc, path)
    if elem.text is None:
        raise TechnicalMetadataError(f"No text found for element at path {path}")
    return elem.text


def get_status(jhove_doc: ET.Element) -> str:
    return retrieve_element_text(jhove_doc, ".//jhove:repInfo/jhove:status")


def get_valid(jhove_doc: ET.Element) -> bool:
    return get_status(jhove_doc) == JHOVE_VALID_OK


def get_mimetype(jhove_doc: ET.Element) -> str:
    return retrieve_element_text(jhove_doc, ".//jhove:repInfo/jhove:mimeType")


def get_niso_mix(jhove_doc: ET.Element) -> str:
    niso_mix_elem = retrieve_element(
        jhove_doc,
        ".//jhove:values[@type='NISOImageMetadata']/jhove:value/mix:mix"
    )
    return ET.tostring(niso_mix_elem, encoding='unicode')


def get_compressed(jhove_doc: ET.Element) -> bool:
    compression = retrieve_element_text(jhove_doc, ".//mix:Compression/mix:compressionScheme")
    return compression != UNCOMPRESSED


def get_rotated(jhove_doc: ET.Element) -> bool:
    orientation_elem = jhove_doc.find(".//mix:ImageCaptureMetadata/mix:orientation", NS_MAP)
    if orientation_elem is None or orientation_elem.text is None: return False
    return ROTATED in orientation_elem.text


def get_jhove_doc(file_path: Path) -> ET.Element:
    try:
        jhove_output = subprocess.run(
            ["/opt/jhove/jhove", "-h", "XML", file_path],
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError as error:
        raise TechnicalMetadataError("JHOVE failed.") from error
    jhove_doc = ET.fromstring(jhove_output.stdout)
    return jhove_doc


def parse_jhove_doc(jhove_doc: ET.Element, file_path: Path) -> TechnicalMetadata:
    if not get_valid(jhove_doc):
        raise TechnicalMetadataError(
            f"File {file_path} was found to be invalid. Status: {get_status(jhove_doc)}"
        )
    
    mimetype_text = get_mimetype(jhove_doc)
    try:
        mimetype = ImageMimetype(mimetype_text)
    except ValueError:
        raise TechnicalMetadataError(f"Unknown mimetype encountered: {mimetype_text}")

    niso_mix_xml = get_niso_mix(jhove_doc)

    compressed = get_compressed(jhove_doc)
    rotated = get_rotated(jhove_doc)

    return TechnicalMetadata(
        mimetype=mimetype,
        metadata=niso_mix_xml,
        metadata_mimetype=TechnicalMetadataMimetype.MIX,
        compressed=compressed,
        rotated=rotated
    )


def get_technical_metadata(file_path: Path) -> TechnicalMetadata:
    jhove_doc = get_jhove_doc(file_path)
    return parse_jhove_doc(jhove_doc, file_path)


def get_fake_technical_metadata(file_path: Path) -> TechnicalMetadata:
    return TechnicalMetadata(
        mimetype=ImageMimetype.JPEG,
        metadata=f"<xml>{file_path}</xml>",
        metadata_mimetype=TechnicalMetadataMimetype.MIX,
        compressed=True
    )
