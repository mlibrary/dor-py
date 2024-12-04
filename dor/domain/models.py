from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinator:
    username: str
    email: str

@dataclass(frozen=True)
class VersionInfo():
    coordinator: Coordinator
    message: str