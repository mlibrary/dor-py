import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytesseract
from PIL import Image


class ImageTextExtractorError(Exception):
    pass


@dataclass
class ImageTextExtractor:
    image_path: Path
    language: str

    @staticmethod
    def list_suppported_languages() -> list[str]:
        return pytesseract.get_languages()

    @classmethod
    def create(cls, image_path: Path, language: str = "eng"):
        if language not in cls.list_suppported_languages():
            raise ImageTextExtractorError("Language code ${language} is not supported.")
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

    ns_map = {"alto": "http://www.loc.gov/standards/alto/ns-v3#"}

    @classmethod
    def create(cls, alto_xml: str):
        return cls(ET.fromstring(alto_xml))

    @staticmethod
    def retrieve_attribute_value(elem: ET.Element, attribute: str):
        value = elem.get(attribute)
        if value is None: raise AltoDocError
        return value

    def __str__(self) -> str:
        return ET.tostring(self.tree, encoding="unicode")

    def find_page_elem(self) -> ET.Element:
        page_elem = self.tree.find(".//alto:Page", self.ns_map)
        if page_elem is None: raise AltoDocError
        return page_elem

    def find_string_elems(self) -> list[ET.Element]:
        return self.tree.findall(".//alto:String", self.ns_map)

    def find_text_line_elems(self) -> list[ET.Element]:
        return self.tree.findall(".//alto:TextLine", self.ns_map)

    @property
    def plain_text(self) -> str:
        text_line_elems = self.find_text_line_elems()
        lines = []
        for text_line_elem in text_line_elems:
            string_elems = text_line_elem.findall("./alto:String", self.ns_map)
            line_words = [
                self.retrieve_attribute_value(string_elem, "CONTENT")
                for string_elem in string_elems
            ]
            line = " ".join(line_words)
            lines.append(line)
        return "\n".join(lines)


@dataclass
class AnnotationData:
    alto_doc: AltoDoc

    strip_punctuation_pattern = re.compile(r"^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$|'s$")

    @staticmethod
    def get_word_coordinates(string_elem: ET.Element) -> list[int]:
        hpos = int(AltoDoc.retrieve_attribute_value(string_elem, "HPOS"))
        vpos = int(AltoDoc.retrieve_attribute_value(string_elem, "VPOS"))
        width = int(AltoDoc.retrieve_attribute_value(string_elem, "WIDTH"))
        height = int(AltoDoc.retrieve_attribute_value(string_elem, "HEIGHT"))
        coordinates = [hpos, vpos, hpos + width, vpos + height]
        return coordinates

    @staticmethod
    def strip_punctuation(word: str) -> str:
        return AnnotationData.strip_punctuation_pattern.sub("", word)

    @property
    def page_dimensions(self) -> dict[str, int]:
        page_elem = self.alto_doc.find_page_elem()
        width = int(self.alto_doc.retrieve_attribute_value(page_elem, "WIDTH"))
        height = int(self.alto_doc.retrieve_attribute_value(page_elem, "HEIGHT"))
        return {"width": width, "height": height}

    @property
    def word_data(self):
        word_data = {}
        for string_elem in self.alto_doc.find_string_elems():
            coordinates = self.get_word_coordinates(string_elem)
            word = self.alto_doc.retrieve_attribute_value(string_elem, "CONTENT")
            normalized_word = self.strip_punctuation(word.lower())
            if normalized_word in word_data:
                word_data[normalized_word].append(coordinates)
            else:
                word_data[normalized_word] = [coordinates]
        return word_data

    @property
    def data(self) -> dict[str, Any]:
        return {
            "page": self.page_dimensions,
            "words": self.word_data
        }
