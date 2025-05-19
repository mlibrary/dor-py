from dataclasses import dataclass, field
from enum import Enum
import pathlib
from importlib import resources

from PIL import ImageFont

RESOURCE_ROOT = resources.files("etc")
FONT_ROOT = RESOURCE_ROOT / "fonts"


@dataclass
class FontFile:
    directory: str = "DepartureMono-1.420"
    family: str = "DepartureMono"
    variant: str = "Regular"
    format: str = "woff2"
    filename: str = f"{family}-{variant}.{format}"

    _path: str = f"{directory}/{filename}"

    def load(self, dpi: int = 72) -> ImageFont.FreeTypeFont:
        with resources.as_file(FONT_ROOT / self._path) as file:
            return ImageFont.truetype(file, dpi)


class ActionChoices(str, Enum):
    store = "store"
    stage = "stage"
    # purge = "purge"


@dataclass
class Settings:
    collid: str = None
    action: ActionChoices = ActionChoices.store
    num_scans: int = -1
    include_desc: bool = True
    include_admin: bool = True
    include_structure: bool = True
    images: bool = True
    texts: bool = True
    total: int = 1
    output_pathname: str = None
    seed: int = -1
    text_font: ImageFont.FreeTypeFont = FontFile().load()

    def update(self, **kw):
        for key, value in kw.items():
            if hasattr(self, key):
                setattr(self, key, value)
        if self.output_pathname is not None:
            self.output_pathname = pathlib.Path(self.output_pathname)


S = Settings()

from jinja2 import Environment, FileSystemLoader, select_autoescape

template_env = Environment(
    loader=FileSystemLoader(
        pathlib.Path(__file__).resolve().parent.parent.joinpath("templates")
    ),
    autoescape=select_autoescape(),
)
