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

class JHOVEParserError(Exception):
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


class JHOVEParser():

    def __init__(self, jhove_doc: ET.Element):
        self.jhove_doc = jhove_doc

    def retrieve_element(self, path: str) -> ET.Element:
        elem = self.jhove_doc.find(path, NS_MAP)
        if elem is None:
            raise JHOVEParserError(f"No element found at path {path}")
        return elem

    def retrieve_element_text(self, path: str) -> str:
        elem = self.retrieve_element(path)
        if elem.text is None:
            raise JHOVEParserError(f"No text found for element at path {path}")
        return elem.text

    def get_status(self) -> str:
        return self.retrieve_element_text(".//jhove:repInfo/jhove:status")

    def get_valid(self) -> bool:
        return self.get_status() == JHOVE_VALID_OK

    def get_mimetype(self) -> str:
        return self.retrieve_element_text(".//jhove:repInfo/jhove:mimeType")

    def get_niso_mix(self) -> str:
        niso_mix_elem = self.retrieve_element(
            ".//jhove:values[@type='NISOImageMetadata']/jhove:value/mix:mix"
        )
        return ET.tostring(niso_mix_elem, encoding='unicode')

    def get_compressed(self) -> bool:
        compression = self.retrieve_element_text(".//mix:Compression/mix:compressionScheme")
        return compression != UNCOMPRESSED

    def get_rotated(self) -> bool:
        orientation_elem = self.jhove_doc.find(".//mix:ImageCaptureMetadata/mix:orientation", NS_MAP)
        if orientation_elem is None or orientation_elem.text is None: return False
        return ROTATED in orientation_elem.text


class TechnicalMetadataGatherer:

    def __init__(self, file_path: Path):
        self.file_path: Path = file_path

    def produce_jhove_doc(self) -> ET.Element:
        try:
            jhove_output = subprocess.run(
                ["/opt/jhove/jhove", "-h", "XML", self.file_path],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as error:
            raise TechnicalMetadataError("JHOVE failed.") from error
        jhove_doc = ET.fromstring(jhove_output.stdout)
        return jhove_doc

    def create_metadata(self, jhove_doc: ET.Element) -> TechnicalMetadata:
        parser = JHOVEParser(jhove_doc)

        if not parser.get_valid():
            raise TechnicalMetadataError(
                f"File {self.file_path} was found to be invalid. " +
                f"Status: {parser.get_status()}"
            )

        mimetype_text = parser.get_mimetype()
        try:
            mimetype = ImageMimetype(mimetype_text)
        except ValueError:
            raise TechnicalMetadataError(f"Unknown mimetype encountered: {mimetype_text}")

        return TechnicalMetadata(
            mimetype=mimetype,
            metadata=parser.get_niso_mix(),
            metadata_mimetype=TechnicalMetadataMimetype.MIX,
            compressed=parser.get_compressed(),
            rotated=parser.get_rotated()
        )

    def gather(self):
        return self.create_metadata(self.produce_jhove_doc())
