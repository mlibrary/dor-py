from dataclasses import dataclass, field

from .persister import Persister
from .query_service import QueryService
from .resource_factory import ResourceFactory

from sqlalchemy import Engine
from sqlalchemy.orm import Session
from .resource import Base

@dataclass
class MetadataAdapter:
    session: Session

    def setup(self):
        Base.metadata.create_all(self.session.get_bind())

    @property
    def persister(self):
        return Persister(adapter=self)

    @property
    def query_service(self):
        return QueryService(adapter=self)

    @property
    def resource_factory(self):
        return ResourceFactory(adapter=self)
    
    def get_column_type(self, column):
        return column.type.compile(dialect=self.session.get_bind().dialect)
