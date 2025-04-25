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
JHOVE_TEXT_METADATA_PROPERTY = "TextMDMetadata"

JHOVE_VALID_OK = "Well-Formed and valid"
UNCOMPRESSED = "Uncompressed"
ROTATED = "rotated"

for prefix in NS_MAP:
    ET.register_namespace(prefix, NS_MAP[prefix])


class JHOVEDocError(Exception):
    pass


class Mimetype(Enum):
    JPEG = "image/jpeg"
    TIFF = "image/tiff"
    JP2 = "image/jp2"
    TXT_ASCII = "text/plain; charset=US-ASCII"
    TXT_UTF8 = "text/plain; charset=UTF-8"
    XML = "text/xml"
    JSON = "application/json"


class TechnicalMetadataMimetype(Enum):
    MIX = "text/xml+mix"
    TEXTMD = "text/xml+textmd"


class JHOVEStatus(Enum):
    VALID_OK = "Well-Formed and valid"


@dataclass
class TechnicalMetadata:
    mimetype: Mimetype
    metadata: ET.Element
    status: JHOVEStatus
    valid: bool

    @classmethod
    def create(cls, file_path: Path) -> "TechnicalMetadata":
        jhove_doc = JHOVEDoc.create(
            file_path,
            cls.metadata_property()
        )

        mimetype = jhove_doc.mimetype
        if mimetype.startswith("image/"):
            cls_ = ImageTechnicalMetadata
        elif mimetype.startswith("text/"):
            cls_ = TextTechnicalMetadata
        else:
            cls_ = cls

        # set the metadata_property
        jhove_doc.metadata_property = cls_.metadata_property()

        return cls_(
            mimetype=Mimetype(jhove_doc.mimetype),
            metadata=jhove_doc.technical_metadata,
            status=JHOVEStatus(jhove_doc.status),
            valid=jhove_doc.valid
        )
    
    @classmethod
    def metadata_property(cls) -> str:
        return "/"

    @property
    def metadata_mimetype(self) -> TechnicalMetadataMimetype:
        raise NotImplementedError

    def __str__(self):
        return ET.tostring(self.metadata, encoding="unicode")

    
@dataclass
class ImageTechnicalMetadata(TechnicalMetadata):
    
    @classmethod
    def metadata_property(cls) -> str:
        return JHOVE_IMAGE_METADATA_PROPERTY

    @property
    def metadata_mimetype(self) -> TechnicalMetadataMimetype:
        return TechnicalMetadataMimetype.MIX

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


@dataclass
class TextTechnicalMetadata(TechnicalMetadata):

    @classmethod
    def metadata_property(cls) -> str:
        return JHOVE_TEXT_METADATA_PROPERTY

    @property
    def metadata_mimetype(self) -> TechnicalMetadataMimetype:
        return TechnicalMetadataMimetype.TEXTMD


class JHOVEDoc:

    @classmethod
    def create(cls, file_path: Path, metadata_property: str) -> Self:
        try:
            jhove_output = subprocess.run(
                ["/opt/jhove/jhove", "-h", "XML", "-c", "./etc/jhove.conf", file_path],
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
        if self.metadata_property == "/":
            return self.jhove_elem
        
        xpath = f'.//jhove:values[@type="{self.metadata_property}"]/jhove:value/*'
        elem = self.retrieve_element(xpath)
        return elem
