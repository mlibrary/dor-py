from dataclasses import dataclass, field
from pydantic import TypeAdapter

from sqlalchemy import select, Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from dor.mockyrie.models import *
from .resource import Resource

from typing import Any



@dataclass
class ResourceFactory:
    # engine: Engine = None
    adapter: Any

    def from_resource(self, resource: Base):
        orm_object = None
        if resource.id:
            try:
                stmt = select(Resource).where(Resource.id==resource.id)
                session = self.adapter.session
                orm_object = session.execute(stmt).one()[0]
                print("found one", orm_object)
            except NoResultFound:
                pass
        if orm_object is None:
            orm_object = Resource(id=resource.id)
            orm_object.created_at = resource.created_at
            orm_object.updated_at = resource.updated_at
            orm_object.internal_resource = resource.__class__.__name__

        data = TypeAdapter(resource.__class__).dump_python(resource)
        for key in [ "id", "created_at", "updated_at" ]:
            data.pop(key)
        orm_object.data = data
        return orm_object

    def to_resource(self, orm_object: Resource):
        cls = globals()[orm_object.internal_resource]
        return cls(
            **( orm_object.data ) | 
            { 
                "id": orm_object.id, 
                "created_at": orm_object.created_at,
                "updated_at": orm_object.updated_at,
                "internal_reosurce": orm_object.internal_resource
            }
        )
