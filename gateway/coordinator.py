from dataclasses import dataclass

@dataclass(frozen=True)
class Coordinator:
    username: str
    email: str
