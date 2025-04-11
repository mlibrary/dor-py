from pathlib import Path

import pytesseract
from PIL import Image


class TesseractImageReaderError(Exception):
    pass


class TesseractImageReader:

    @staticmethod
    def list_suppported_languages() -> list[str]:
        return pytesseract.get_languages()

    def __init__(self, image_path: Path, language: str="eng"):
        self.image_path: Path = image_path
        self.language = language

        if language not in self.list_suppported_languages():
            raise TesseractImageReaderError("Language code ${language} is not supported.")

    @property
    def text(self) -> str:
        return pytesseract.image_to_string(Image.open(self.image_path), lang=self.language)


