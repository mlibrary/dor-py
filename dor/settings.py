from dataclasses import dataclass, field
from enum import Enum
import pathlib

from PIL import ImageFont


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

text_font = ImageFont.truetype(
    pathlib.Path(__file__)
    .resolve()
    .parent.parent.joinpath("etc/fonts/DepartureMono-1.420/DepartureMono-Regular.woff2"),
    72,
)
