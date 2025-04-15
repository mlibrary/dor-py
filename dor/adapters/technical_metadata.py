import subprocess
from typing import Self
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

JHOVE_NS = "http://schema.openpreservation.org/ois/xml/ns/jhove"
MIX_NS = "http://www.loc.gov/mix/v20"
NS_MAP = {'jhove': JHOVE_NS, 'mix': MIX_NS}

JHOVE_IMAGE_METADATA_PROPERTY = "NISOImageMetadata"

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
    status: JHOVEStatus
    valid: bool

    @classmethod
    def create(cls, file_path: Path) -> Self:
        jhove_doc = JHOVEDoc.create(
            file_path,
            JHOVE_IMAGE_METADATA_PROPERTY
        )

        return cls(
            mimetype=ImageMimetype(jhove_doc.mimetype),
            metadata=jhove_doc.technical_metadata,
            status=JHOVEStatus(jhove_doc.status),
            valid=jhove_doc.valid
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

    def __str__(self):
        return ET.tostring(self.metadata, encoding="unicode")


class JHOVEDoc:

    @classmethod
    def create(cls, file_path: Path, metadata_property: str) -> Self:
        try:
            jhove_output = subprocess.run(
                ["/opt/jhove/jhove", "-h", "XML", file_path],
                capture_output=True,
                check=True
            )
        except subprocess.CalledProcessError as error:
            raise JHOVEDocError("JHOVE failed.") from error
        jhove_elem = ET.fromstring(jhove_output.stdout)
        return cls(jhove_elem, metadata_property)

    def __init__(self, jhove_elem: ET.Element, metadata_property: str):
        self.jhove_elem = jhove_elem
        self.metadata_property = metadata_property

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
    
    @property
    def technical_metadata(self) -> ET.Element:
        xpath = f'.//jhove:values[@type="{self.metadata_property}"]/jhove:value/*'
        elem = self.retrieve_element(xpath)
        return elem
