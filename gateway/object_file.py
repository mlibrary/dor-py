from dataclasses import dataclass

@dataclass(frozen=True)
class ObjectFile:
    logical_path: str
    literal_path: str
