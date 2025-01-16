# from dor.domain.models import Bin
from abc import ABC, abstractmethod
from dor.domain import models

import uuid

from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy import (
    Column, String, select, Table, Uuid
)
from sqlalchemy.orm import registry

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.mutable import MutableList
import sqlalchemy.exc

from pydantic_core import to_jsonable_python
import json

from dor.providers.models import PackageResource

mapper_registry = registry()

def _custom_json_serializer(*args, **kwargs) -> str:
    """
    Encodes json in the same way that pydantic does.
    """
    return json.dumps(*args, default=to_jsonable_python, **kwargs)

class Base(DeclarativeBase):
    pass

class Bin(Base):
    __tablename__ = "catalog_bin"

    identifier: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    alternate_identifiers: Mapped[list] = Column(MutableList.as_mutable(ARRAY(String)))
    common_metadata: Mapped[dict] = mapped_column(JSONB)
    package_resources: Mapped[dict] = mapped_column(JSONB)

    # created_at: Mapped[datetime.datetime] = mapped_column(
    #     DateTime(timezone=True), server_default=func.now()
    # )
    # updated_at: Mapped[datetime.datetime] = mapped_column(
    #     DateTime(timezone=True), server_default=func.now()
    # )


class Catalog(ABC):

    @abstractmethod
    def add(self, bin: models.Bin):
        raise NotImplementedError

    @abstractmethod
    def get(self, identifier: str):
        raise NotImplementedError

    @abstractmethod
    def get_by_alternate_identifier(self, identifier: str):
        raise NotImplementedError


class MemoryCatalog(Catalog):
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


class SqlalchemyCatalog(Catalog):
    
    def __init__(self, session):
        self.session = session

    def add(self, bin: models.Bin):
        stored_bin = Bin(
            identifier=bin.identifier,
            alternate_identifiers=bin.alternate_identifiers,
            common_metadata=bin.common_metadata,
            package_resources=bin.package_resources
        )
        self.session.add(stored_bin)

    def get(self, identifier) -> models.Bin | None:
        statement = select(Bin).where(Bin.identifier == identifier)
        return self._fetch_one(statement)

    def get_by_alternate_identifier(self, identifier: str) -> Bin | None:
        statement = select(Bin).filter(Bin.alternate_identifiers.contains([identifier]))
        return self._fetch_one(statement)

    def _fetch_one(self, statement):
        try:
            result = self.session.scalars(statement).one()
            bin = models.Bin(
                identifier=result.identifier,
                alternate_identifiers=result.alternate_identifiers,
                common_metadata=result.common_metadata,
                package_resources=result.package_resources
            )
            return bin
        except sqlalchemy.exc.NoResultFound:
            return None
