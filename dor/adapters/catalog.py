import uuid
from abc import ABC, abstractmethod
from datetime import datetime

import sqlalchemy.exc
from sqlalchemy import (
    Column, DateTime, Integer, select, String, Uuid
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
    revision_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    common_metadata: Mapped[dict] = mapped_column(JSONB)
    package_resources: Mapped[dict] = mapped_column(JSONB)


class CurrentRevision(Base):
    __tablename__ = "catalog_current_revision"

    identifier: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    alternate_identifiers: Mapped[list] = Column(MutableList.as_mutable(ARRAY(String)))
    revision_number: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    common_metadata: Mapped[dict] = mapped_column(JSONB)
    package_resources: Mapped[dict] = mapped_column(JSONB)


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
        
    def get(self, identifier: str):
        latest_revision = None
        for revision in self.revisions:
            if (
                str(revision.identifier) == identifier and \
                (latest_revision is None or latest_revision.revision_number < revision.revision_number)
            ):
                latest_revision = revision
        return latest_revision
    
    def get_by_alternate_identifier(self, identifier: str):
        latest_revision = None
        for revision in self.revisions:
            if (
                identifier in revision.alternate_identifiers and \
                (latest_revision is None or latest_revision.revision_number < revision.revision_number)
            ):
                latest_revision = revision
        return latest_revision


class SqlalchemyCatalog(Catalog):
    
    def __init__(self, session):
        self.session = session

    def add(self, revision: models.Revision):
        # Create new Revision record
        stored_revision = Revision(
            identifier=revision.identifier,
            alternate_identifiers=revision.alternate_identifiers,
            revision_number=revision.revision_number,
            created_at=revision.created_at,
            common_metadata=revision.common_metadata,
            package_resources=revision.package_resources
        )

        # Update or insert new CurrentRevision record
        statement = select(CurrentRevision).where(CurrentRevision.identifier == revision.identifier)
        try:
            stored_current_revision = self.session.scalars(statement).one()
            stored_current_revision.alternate_identifiers = revision.alternate_identifiers
            stored_current_revision.revision_number = revision.revision_number
            stored_current_revision.created_at = revision.created_at
            stored_current_revision.common_metadata = revision.common_metadata
            stored_current_revision.package_resources = revision.package_resources
        except sqlalchemy.exc.NoResultFound:
            stored_current_revision = CurrentRevision(
                identifier=revision.identifier,
                alternate_identifiers=revision.alternate_identifiers,
                revision_number=revision.revision_number,
                created_at=revision.created_at,
                common_metadata=revision.common_metadata,
                package_resources=revision.package_resources
            )
        self.session.add_all([stored_revision, stored_current_revision])

    def get(self, identifier) -> models.Revision | None:
        statement = select(CurrentRevision).where(CurrentRevision.identifier == identifier)
        return self._fetch_one(statement)

    def get_by_alternate_identifier(self, identifier: str) -> models.Revision | None:
        statement = select(CurrentRevision).filter(CurrentRevision.alternate_identifiers.contains([identifier]))
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
