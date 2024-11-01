from dataclasses import dataclass, field
from typing import Mapping

# from .metadata_adapter import MetadataAdapter
from dor.mockyrie.models import Base

from sqlalchemy.orm import Session
from sqlalchemy import Engine

@dataclass
class Persister:
    adapter: 'MetadataAdapter'

    def save(self, resource: Base):
        with self.adapter.session as session:
            orm_object = self.adapter.resource_factory.from_resource(resource=resource)
            session.add(orm_object)
            session.commit()
            print("persister.save", orm_object)
        return self.adapter.resource_factory.to_resource(orm_object=orm_object)
