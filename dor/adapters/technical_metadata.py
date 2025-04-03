import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

JHOVE_NS = "http://schema.openpreservation.org/ois/xml/ns/jhove"
MIX_NS = "http://www.loc.gov/mix/v20"
NS_MAP = {'jhove': JHOVE_NS, 'mix': MIX_NS}

JHOVE_VALID_OK = "Well-Formed and valid"
UNCOMPRESSED = "Uncompressed"
ROTATED = "rotated"

ACCEPTED_IMAGE_MIMETYPES = [
    "image/jpeg",
    "image/tiff",
    "image/jp2",
]

for prefix in NS_MAP:
    ET.register_namespace(prefix, NS_MAP[prefix])


class TechnicalMetadataError(Exception):
    pass


@dataclass
class TechnicalMetadata:
    mimetype: str
    metadata: str
    metadata_mimetype: str
    rotated: bool = False
    compressed: bool = False


def get_technical_metadata(file_path: Path) -> TechnicalMetadata:
    try:
        jhove_output = subprocess.run(["/opt/jhove/jhove", "-h", "XML", file_path], capture_output=True)
    except subprocess.SubprocessError as error:
        raise TechnicalMetadataError("JHOVE failed.") from error
    jhove_doc = ET.fromstring(jhove_output.stdout)

    status_elem = jhove_doc.find(f".//jhove:repInfo/jhove:status", NS_MAP)
    if status_elem is None or status_elem.text is None: raise TechnicalMetadataError
    status = status_elem.text
    if status != JHOVE_VALID_OK:
        raise TechnicalMetadataError(f"File {file_path} was found to be invalid. Status: {status}")
    
    mimetype_elem = jhove_doc.find(f".//jhove:repInfo/jhove:mimeType", NS_MAP)
    if mimetype_elem is None or mimetype_elem.text is None: raise TechnicalMetadataError
    mimetype = mimetype_elem.text
    if not mimetype in ACCEPTED_IMAGE_MIMETYPES:
        raise TechnicalMetadataError(f"File {file_path} has an unexpected file type: {mimetype}")

    niso_mix_elem = jhove_doc.find(
        f".//jhove:values[@type='NISOImageMetadata']/jhove:value/mix:mix", NS_MAP
    )
    if niso_mix_elem is None: raise TechnicalMetadataError
    niso_mix_xml = ET.tostring(niso_mix_elem, encoding='unicode')

    compression_elem = niso_mix_elem.find(".//mix:Compression/mix:compressionScheme", NS_MAP)
    if compression_elem is None or compression_elem.text is None:
        raise TechnicalMetadataError
    compressed = compression_elem.text != UNCOMPRESSED

    orientation_elem = niso_mix_elem.find(".//mix:ImageCaptureMetadata/mix:orientation", NS_MAP)
    if orientation_elem is None or orientation_elem.text is None:
        rotated = False
    else:
        rotated = ROTATED in orientation_elem.text

    return TechnicalMetadata(
        mimetype=mimetype,
        metadata=niso_mix_xml,
        metadata_mimetype="text/xml+mix",
        compressed=compressed,
        rotated=rotated
    )


def get_fake_technical_metadata(file_path: Path) -> TechnicalMetadata:
    return TechnicalMetadata(mimetype="image/jpeg", metadata=f"<xml>{file_path}</xml>", metadata_mimetype="text/xml+mix")
