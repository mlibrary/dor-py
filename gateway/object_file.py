from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class ObjectFile:
    logical_path: Path
    literal_path: Path
