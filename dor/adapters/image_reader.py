import xml.etree.ElementTree as ET
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytesseract
from PIL import Image


class TesseractImageReaderError(Exception):
    pass


@dataclass
class TesseractImageReader:
    image_path: Path
    language: str

    @staticmethod
    def list_suppported_languages() -> list[str]:
        return pytesseract.get_languages()

    @classmethod
    def create(cls, image_path: Path, language: str = "eng"):
        if language not in cls.list_suppported_languages():
            raise TesseractImageReaderError("Language code ${language} is not supported.")
        return cls(image_path=image_path, language=language)

    @property
    def text(self) -> str:
        return pytesseract.image_to_string(Image.open(self.image_path), lang=self.language)

    @property
    def alto(self) -> str:
        result = pytesseract.image_to_alto_xml(Image.open(self.image_path), lang=self.language)
        if isinstance(result, bytes):
            return result.decode()
        return str(result)


class AltoDocError(Exception):
    pass


@dataclass
class AltoDoc:
    tree: ET.Element

    strip_punctuation_pattern = re.compile(r"^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$|'s$")
    ns_map = {"alto": "http://www.loc.gov/standards/alto/ns-v3#"}

    @classmethod
    def create(cls, alto_xml: str):
        return cls(ET.fromstring(alto_xml))

    def __str__(self) -> str:
        return ET.tostring(self.tree, encoding="unicode")

    @staticmethod
    def retrieve_attribute_value(elem: ET.Element, attribute: str):
        value = elem.get(attribute)
        if value is None: raise AltoDocError
        return value

    @staticmethod
    def get_word_coordinates(elem: ET.Element) -> list[int]:
        hpos = int(AltoDoc.retrieve_attribute_value(elem, "HPOS"))
        vpos = int(AltoDoc.retrieve_attribute_value(elem, "VPOS"))
        width = int(AltoDoc.retrieve_attribute_value(elem, "WIDTH"))
        height = int(AltoDoc.retrieve_attribute_value(elem, "HEIGHT"))
        coordinates = [hpos, vpos, hpos + width, vpos + height]
        return coordinates

    @staticmethod
    def strip_punctuation(word: str) -> str:
        return AltoDoc.strip_punctuation_pattern.sub("", word)

    @property
    def page_dimensions(self) -> dict[str, int]:
        page_elem = self.tree.find(".//alto:Page", self.ns_map)
        if page_elem is None: raise AltoDocError
        width = int(self.retrieve_attribute_value(page_elem, "WIDTH"))
        height = int(self.retrieve_attribute_value(page_elem, "HEIGHT"))
        return {"width": width, "height": height}

    @property
    def word_data(self):
        word_data = {}
        word_elems = self.tree.findall(".//alto:String", self.ns_map)
        for word_elem in word_elems:
            coordinates = self.get_word_coordinates(word_elem)
            word = self.retrieve_attribute_value(word_elem, "CONTENT")
            normalized_word = self.strip_punctuation(word.lower())
            if normalized_word in word_data:
                word_data[normalized_word].append(coordinates)
            else:
                word_data[normalized_word] = [coordinates]
        return word_data

    @property
    def annotation_data(self) -> dict[str, Any]:
        return {
            "page": self.page_dimensions,
            "words": self.word_data
        }
