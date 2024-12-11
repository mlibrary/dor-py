from dataclasses import dataclass

from gateway.coordinator import Coordinator

@dataclass(frozen=True)
class VersionInfo():
    coordinator: Coordinator
    message: str
