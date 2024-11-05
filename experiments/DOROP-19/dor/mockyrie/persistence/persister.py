from dataclasses import dataclass, field
from typing import Mapping

from dor.mockyrie.models import Base

import logging


@dataclass
class Persister:
    adapter: 'MetadataAdapter'

    def save(self, resource: Base):
        with self.adapter.session as session:
            orm_object = self.adapter.resource_factory.from_resource(resource=resource)
            session.add(orm_object)
            session.commit()
            logging.info(f"persister.save: {orm_object.id} {resource.__class__.__name__} saved")
        return self.adapter.resource_factory.to_resource(orm_object=orm_object)
