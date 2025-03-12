from dataclasses import dataclass

from datetime import datetime

@dataclass(frozen=True)
class VersionInfo:
    version: int
    author: str
    date: datetime
    message: str

    
