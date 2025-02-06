import uuid
from abc import ABC, abstractmethod
from datetime import datetime

import sqlalchemy.exc
from sqlalchemy import (
    Column, DateTime, String, select, Uuid
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.mutable import MutableList

from dor.adapters.sqlalchemy import Base
from dor.domain import models


class Version(Base):
    __tablename__ = "catalog_version"

    identifier: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    alternate_identifiers: Mapped[list] = Column(MutableList.as_mutable(ARRAY(String)))
    version_number: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    common_metadata: Mapped[dict] = mapped_column(JSONB)
    package_resources: Mapped[dict] = mapped_column(JSONB)


    # updated_at: Mapped[datetime.datetime] = mapped_column(
    #     DateTime(timezone=True), server_default=func.now()
    # )


class Catalog(ABC):

    @abstractmethod
    def add(self, version: models.Version):
        raise NotImplementedError

    @abstractmethod
    def get(self, identifier: str):
        raise NotImplementedError

    @abstractmethod
    def get_by_alternate_identifier(self, identifier: str):
        raise NotImplementedError


class MemoryCatalog(Catalog):
    def __init__(self):
        self.versions = []
        
    def add(self, version):
        self.versions.append(version)
        
    def get(self, identifier):
        for version in self.versions:
            if version.identifier == identifier:
                return version
        return None
    
    def get_by_alternate_identifier(self, identifier):
        for version in self.versions:
            if identifier in version.alternate_identifiers:
                return version
        return None


class SqlalchemyCatalog(Catalog):
    
    def __init__(self, session):
        self.session = session

    def add(self, version: models.Version):
        stored_version = Version(
            identifier=version.identifier,
            alternate_identifiers=version.alternate_identifiers,
            version_number=version.version_number,
            created_at=version.created_at,
            common_metadata=version.common_metadata,
            package_resources=version.package_resources
        )
        self.session.add(stored_version)

    def get(self, identifier) -> models.Version | None:
        statement = select(Version).where(Version.identifier == identifier)
        return self._fetch_one(statement)

    def get_by_alternate_identifier(self, identifier: str) -> models.Version | None:
        statement = select(Version).filter(Version.alternate_identifiers.contains([identifier]))
        return self._fetch_one(statement)

    def _fetch_one(self, statement):
        try:
            result = self.session.scalars(statement).one()
            version = models.Version(
                identifier=result.identifier,
                alternate_identifiers=result.alternate_identifiers,
                version_number=result.version_number,
                created_at=result.created_at,
                common_metadata=result.common_metadata,
                package_resources=result.package_resources
            )
            return version
        except sqlalchemy.exc.NoResultFound:
            return None
