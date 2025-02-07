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


class Revision(Base):
    __tablename__ = "catalog_revision"

    identifier: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    alternate_identifiers: Mapped[list] = Column(MutableList.as_mutable(ARRAY(String)))
    revision_number: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    common_metadata: Mapped[dict] = mapped_column(JSONB)
    package_resources: Mapped[dict] = mapped_column(JSONB)

    # updated_at: Mapped[datetime.datetime] = mapped_column(
    #     DateTime(timezone=True), server_default=func.now()
    # )


class Catalog(ABC):

    @abstractmethod
    def add(self, revision: models.Revision):
        raise NotImplementedError

    @abstractmethod
    def get(self, identifier: str):
        raise NotImplementedError

    @abstractmethod
    def get_by_alternate_identifier(self, identifier: str):
        raise NotImplementedError


class MemoryCatalog(Catalog):
    def __init__(self):
        self.revisions = []
        
    def add(self, revision):
        self.revisions.append(revision)
        
    def get(self, identifier):
        for revision in self.revisions:
            if revision.identifier == identifier:
                return revision
        return None
    
    def get_by_alternate_identifier(self, identifier):
        for revision in self.revisions:
            if identifier in revision.alternate_identifiers:
                return revision
        return None


class SqlalchemyCatalog(Catalog):
    
    def __init__(self, session):
        self.session = session

    def add(self, revision: models.Revision):
        stored_revision = Revision(
            identifier=revision.identifier,
            alternate_identifiers=revision.alternate_identifiers,
            revision_number=revision.revision_number,
            created_at=revision.created_at,
            common_metadata=revision.common_metadata,
            package_resources=revision.package_resources
        )
        self.session.add(stored_revision)

    def get(self, identifier) -> models.Revision | None:
        statement = select(Revision).where(Revision.identifier == identifier)
        return self._fetch_one(statement)

    def get_by_alternate_identifier(self, identifier: str) -> models.Revision | None:
        statement = select(Revision).filter(Revision.alternate_identifiers.contains([identifier]))
        return self._fetch_one(statement)

    def _fetch_one(self, statement):
        try:
            result = self.session.scalars(statement).one()
            revision = models.Revision(
                identifier=result.identifier,
                alternate_identifiers=result.alternate_identifiers,
                revision_number=result.revision_number,
                created_at=result.created_at,
                common_metadata=result.common_metadata,
                package_resources=result.package_resources
            )
            return revision
        except sqlalchemy.exc.NoResultFound:
            return None
