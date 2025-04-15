import subprocess
from typing import Self
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


class JHOVEDocError(Exception):
    pass


class ImageMimetype(Enum):
    JPEG = "image/jpeg"
    TIFF = "image/tiff"
    JP2 = "image/jp2"


class TechnicalMetadataMimetype(Enum):
    MIX = "text/xml+mix"


class JHOVEStatus(Enum):
    VALID_OK = "Well-Formed and valid"


@dataclass
class ImageTechnicalMetadata:
    mimetype: ImageMimetype
    metadata: ET.Element
    # metadata_mimetype: TechnicalMetadataMimetype
    # rotated: bool = False
    # compressed: bool = False

    @classmethod
    def create(cls, file_path: Path) -> Self:
        input = JHOVEDoc.create(
            file_path,
            'NISOImageMetadata'
            # "jhove:values[@type='NISOImageMetadata']/jhove:value/mix:mix"
        )

        return cls(
            mimetype=ImageMimetype(input.mimetype),
            metadata=input.technical_metadata,
        )
    
    @property
    def rotated(self) -> bool:
        orientation_elem = self.metadata.find(".//mix:ImageCaptureMetadata/mix:orientation", NS_MAP)
        if orientation_elem is None or orientation_elem.text is None: return False
        return ROTATED in orientation_elem.text

    @property
    def compressed(self) -> bool:
        compression_elem = self.metadata.find(".//mix:Compression/mix:compressionScheme", NS_MAP)
        if compression_elem is None:
            return False
        return compression_elem.text != UNCOMPRESSED
    
    @property
    def metadata_mimetype(self) -> TechnicalMetadataMimetype:
        return TechnicalMetadataMimetype.MIX



@dataclass
class JHOVEData:
    status: JHOVEStatus
    mimetype: str
    technical_metadata: ET.Element

class JHOVEDoc:

    @classmethod
    def create(cls, file_path: Path, xpath: str) -> Self:
        try:
            jhove_output = subprocess.run(
                ["/opt/jhove/jhove", "-h", "XML", file_path],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as error:
            raise JHOVEDocError("JHOVE failed.") from error
        jhove_elem = ET.fromstring(jhove_output.stdout)
        return cls(jhove_elem, xpath).data()

    def __init__(self, jhove_elem: ET.Element, xpath: str):
        self.jhove_elem = jhove_elem
        self.xpath = xpath

    def retrieve_element(self, path: str) -> ET.Element:
        elem = self.jhove_elem.find(path, NS_MAP)
        if elem is None:
            raise JHOVEDocError(f"No element found at path {path}")
        return elem

    def retrieve_element_text(self, path: str) -> str:
        elem = self.retrieve_element(path)
        if elem.text is None:
            raise JHOVEDocError(f"No text found for element at path {path}")
        return elem.text

    @property
    def status(self) -> str:
        return self.retrieve_element_text(".//jhove:repInfo/jhove:status")

    @property
    def valid(self) -> bool:
        return self.status == JHOVE_VALID_OK

    @property
    def mimetype(self) -> str:
        return self.retrieve_element_text(".//jhove:repInfo/jhove:mimeType")
    
    def data(self) -> JHOVEData:
        return JHOVEData(
            status=JHOVEStatus(self.status),
            mimetype=self.mimetype,
            technical_metadata=self.technical_metadata
        )

    @property
    def technical_metadata(self) -> ET.Element:
        xpath = f'.//jhove:values[@type="{self.xpath}"]/jhove:value/*'
        elem = self.retrieve_element(
            xpath
        )
        return elem

    @property
    def niso_mix(self) -> str:
        niso_mix_elem = self.retrieve_element(
            ".//jhove:values[@type='NISOImageMetadata']/jhove:value/mix:mix"
        )
        return ET.tostring(niso_mix_elem, encoding='unicode')

    @property
    def compressed(self) -> bool:
        compression = self.retrieve_element_text(".//mix:Compression/mix:compressionScheme")
        return compression != UNCOMPRESSED

    @property
    def rotated(self) -> bool:
        orientation_elem = self.jhove_elem.find(".//mix:ImageCaptureMetadata/mix:orientation", NS_MAP)
        if orientation_elem is None or orientation_elem.text is None: return False
        return ROTATED in orientation_elem.text

    # @property
    # def technical_metadata(self) -> TechnicalMetadata:
    #     if not self.valid:
    #         raise JHOVEDocError(f"File was found to be invalid. Status: {self.status}")

    #     mimetype_text = self.mimetype
    #     try:
    #         mimetype = ImageMimetype(mimetype_text)
    #     except ValueError:
    #         raise JHOVEDocError(f"Unknown mimetype encountered: {mimetype_text}")

    #     return TechnicalMetadata(
    #         mimetype=mimetype,
    #         metadata=self.niso_mix,
    #         metadata_mimetype=TechnicalMetadataMimetype.MIX,
    #         compressed=self.compressed,
    #         rotated=self.rotated
    #     )

