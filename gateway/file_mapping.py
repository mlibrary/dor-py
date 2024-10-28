from dataclasses import dataclass

@dataclass(frozen=True)
class FileMapping:
    logical_path: str
    literal_path: str
