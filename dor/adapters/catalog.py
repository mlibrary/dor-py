from dor.domain.models import Bin

from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy import (
    Column, String, select, Table, Uuid
)
from sqlalchemy.orm import registry
import pydantic.json
import json

mapper_registry = registry()

def _custom_json_serializer(*args, **kwargs) -> str:
    """
    Encodes json in the same way that pydantic does.
    """
    return json.dumps(*args, default=pydantic.json.pydantic_encoder, **kwargs)

bin_table = Table(
    "catalog_bin",
    mapper_registry.metadata,
    Column("identifier", Uuid, primary_key=True),
    Column("alternate_identifiers", ARRAY(String)),
    Column("common_metadata", JSONB),
    Column("package_resources", JSONB)
)


class MemoryCatalog:
    def __init__(self):
        self.bins = []
        
    def add(self, bin):
        self.bins.append(bin)
        
    def get(self, identifier):
        for bin in self.bins:
            if bin.identifier == identifier:
                return bin 
        return None
    
    def get_by_alternate_identifier(self, identifier):
        for bin in self.bins:
            if identifier in bin.alternate_identifiers:
                return bin 
        return None


class SqlalchemyCatalog:
    
    def __init__(self, session):
        self.session = session

    def add(self, bin: Bin):
        self.session.add(bin)

    def get(self, identifier) -> Bin | None:
        statement = select(Bin).where(Bin.identifier == identifier)
        results = self.session.execute(statement).one()
        if len(results) == 1:
            return results[0]
        return None


def start_mappers() -> None:
    mapper_registry.map_imperatively(Bin, bin_table)