import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

from metadata.exceptions import DataNotFoundError

class ElementAdapter():

    @classmethod
    def from_string(cls, text: str, namespaces: dict[str, str]) -> "ElementAdapter":
        return cls(ET.fromstring(text=text), namespaces)

    def __init__(self, elem: Element, namespaces: dict[str, str]):
        self.elem = elem
        self.namespaces = namespaces

    def find(self, path: str) -> "ElementAdapter":
        result = self.elem.find(path, self.namespaces)
        if result is None:
            raise DataNotFoundError()
        return ElementAdapter(result, self.namespaces)
    
    @property
    def text(self) -> str:
        result = self.elem.text
        if result is None:
            raise DataNotFoundError()
        return result

    def get(self, key: str) -> str:
        result = self.elem.get(key)
        if result is None:
            raise DataNotFoundError()
        return result

    def findall(self, path: str) -> "list[ElementAdapter]":
        return [
            ElementAdapter(elem, self.namespaces)
            for elem in self.elem.findall(path, self.namespaces)
        ]
    
    @property
    def tag(self) -> str:
        return self.elem.tag

    def get_children(self) -> "list[ElementAdapter]":
        return [ElementAdapter(elem, self.namespaces) for elem in self.elem[:]]
