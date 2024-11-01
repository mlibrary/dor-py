import dataclasses
from pydantic.dataclasses import dataclass
from pydantic import Field
from typing import Dict, List

import datetime

class Base:
    pass

@dataclass
class Asset(Base):
    id: int = None
    # created_at: datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
    # updated_at: datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.UTC))
    created_at: datetime.datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: datetime.datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )

    metadata: Dict[str, dict] = dataclasses.field(default_factory=lambda: {})
    file_metadata: List[Dict[str, list]] = dataclasses.field(default_factory=lambda: [])

    alternate_ids: list = dataclasses.field(default_factory=list)

@dataclass
class Monograph(Base):
    id: int = None

    created_at: datetime.datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: datetime.datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )

    metadata: Dict[str, dict] = dataclasses.field(default_factory=lambda: {})
    logical_structure: list = dataclasses.field(default_factory=list)
    member_ids: list = dataclasses.field(default_factory=list)

    alternate_ids: list = dataclasses.field(default_factory=list)
