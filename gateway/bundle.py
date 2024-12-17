from dataclasses import dataclass
from pathlib import Path


@dataclass
class Bundle:
    root_path: Path
    entries: list[Path]
