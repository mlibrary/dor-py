from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class Command:
    pass

@dataclass
class CreatePackage(Command):
    type = "package.create"
    deposit_group_identifier: str
    date: str
    package_metadata: dict[str, Any]


@dataclass
class DepositPackage(Command):
    type = 'package.deposit'
    package_identifier: str

