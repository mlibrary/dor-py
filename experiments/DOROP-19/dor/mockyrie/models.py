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
    created_at: datetime.datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )
    updated_at: datetime.datetime = dataclasses.field(
        default_factory=lambda: datetime.datetime.now(datetime.UTC)
    )

    metadata: Dict[str, dict] = dataclasses.field(default_factory=lambda: {})
    file_metadata: List[Dict[str, list]] = dataclasses.field(default_factory=lambda: [])

    alternate_ids: list = dataclasses.field(default_factory=list)

    # IRL assets do not have common metadata
    @property
    def title(self):
        return self.metadata['common']['title']

    def __repr__(self):
        return f"<[{self.id}] {self.__class__.__name__} : {self.title}>"
    
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

    @property
    def title(self):
        return self.metadata['common']['title']
    
    def __repr__(self):
        return f"<[{self.id}]{self.summarize_alternate_ids()} {self.__class__.__name__} : {self.title}>"
    
    def summarize_alternate_ids(self):
        if not self.alternate_ids:
            return ""
        return " {" + "/".join([a['id'] for a in self.alternate_ids]) + '}'
