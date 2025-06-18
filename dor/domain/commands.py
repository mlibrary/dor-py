from dataclasses import dataclass
from datetime import datetime
from typing import Any

@dataclass
class Command:
    pass

@dataclass
class CreateFileset(Command):
    type = "fileset.create"
    project_id: str
    file_name: str
    job_idx: int
    file_profiles: dict[str, list[str]]


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

