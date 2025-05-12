import uuid
from abc import ABC, abstractmethod
from datetime import datetime

import sqlalchemy.exc
from sqlalchemy import (
    Column, DateTime, Index, Integer, cast, or_, select, String, Uuid
)
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.ext.mutable import MutableList

from dor.adapters.converter import converter
from dor.adapters.sqlalchemy import Base
from dor.builders.parts import UseFunction
from dor.domain import models
from dor.providers.models import PackageResource, AlternateIdentifier


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

    __table_args__ = (
        Index(
            'index_catalog_on_package_resources_jsonb_path_ops_idx',  # Give your index a meaningful name
            package_resources,
            postgresql_using='gin',
            postgresql_ops={'payload': 'jsonb_path_ops'}
        ),
    )


class Catalog(ABC):

    @abstractmethod
    def add(self, revision: models.Revision) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, identifier: str) -> models.Revision | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_alternate_identifier(self, identifier: str) -> models.Revision | None:
        raise NotImplementedError

    @abstractmethod
    def find_by_file_set(self, file_set_identifier: str) -> list[models.Revision]:
        raise NotImplementedError

    @abstractmethod
    def get_revisions(self, identifier: str) -> list[models.Revision]:
        raise NotImplementedError


class MemoryCatalog(Catalog):
    def __init__(self):
        self.revisions = []

    def add(self, revision: models.Revision) -> None:
        self.revisions.append(revision)

    def get(self, identifier: str) -> models.Revision | None:
        latest_revision = None
        for revision in self.revisions:
            if (
                str(revision.identifier) == identifier and
                (latest_revision is None or revision.revision_number > latest_revision.revision_number)
            ):
                latest_revision = revision
        return latest_revision

    def get_by_alternate_identifier(self, identifier: str) -> models.Revision | None:
        latest_revision = None
        for revision in self.revisions:
            if (
                identifier in revision.alternate_identifiers and
                (latest_revision is None or revision.revision_number > latest_revision.revision_number)
            ):
                latest_revision = revision
        return latest_revision

    def find_by_file_set(self, requested_identifier: str) -> list[models.Revision]:
        revisions = []
        file_set_identifier = uuid.UUID(requested_identifier)
        referenced_file_set_identifier = AlternateIdentifier(
            type=UseFunction.copy_of.value,
            id=requested_identifier
        )
        for revision in self.revisions:
            for resource in revision.package_resources:
                if resource.id == file_set_identifier:
                    revisions.append(revision)
                elif resource.has_alternate_identifier(referenced_file_set_identifier):
                    revisions.append(revision)

        return revisions

    def get_revisions(self, identifier: str) -> list[models.Revision]:
        return [revision for revision in self.revisions if str(revision.identifier) == identifier]


class SqlalchemyCatalog(Catalog):

    def __init__(self, session):
        self.session = session

    def add(self, revision: models.Revision) -> None:
        package_resources_data = converter.unstructure(revision.package_resources)

        # Create new Revision record
        stored_revision = Revision(
            identifier=revision.identifier,
            alternate_identifiers=revision.alternate_identifiers,
            revision_number=revision.revision_number,
            created_at=revision.created_at,
            common_metadata=revision.common_metadata,
            package_resources=package_resources_data
        )

        # Update or create new CurrentRevision record
        statement = select(CurrentRevision).where(CurrentRevision.identifier == revision.identifier)
        try:
            stored_current_revision = self.session.scalars(statement).one()
            stored_current_revision.alternate_identifiers = revision.alternate_identifiers
            stored_current_revision.revision_number = revision.revision_number
            stored_current_revision.created_at = revision.created_at
            stored_current_revision.common_metadata = revision.common_metadata
            stored_current_revision.package_resources = package_resources_data
        except sqlalchemy.exc.NoResultFound:
            stored_current_revision = CurrentRevision(
                identifier=revision.identifier,
                alternate_identifiers=revision.alternate_identifiers,
                revision_number=revision.revision_number,
                created_at=revision.created_at,
                common_metadata=revision.common_metadata,
                package_resources=package_resources_data
            )
        self.session.add_all([stored_revision, stored_current_revision])

    def get(self, identifier: str) -> models.Revision | None:
        statement = select(CurrentRevision).where(CurrentRevision.identifier == identifier)
        return self._fetch_one(statement)

    def get_by_alternate_identifier(self, identifier: str) -> models.Revision | None:
        statement = select(CurrentRevision).filter(CurrentRevision.alternate_identifiers.contains([identifier]))
        return self._fetch_one(statement)

    def find_by_file_set(self, requested_identifier: str) -> list[models.Revision]:
        statement = select(CurrentRevision).where(
            or_(
                CurrentRevision.package_resources.op('@>')(
                    cast([{"type": "File Set", "id": requested_identifier}], JSONB)
                ),
                CurrentRevision.package_resources.op('@>')(
                    cast([{
                        "type": "File Set",
                        "alternate_identifiers": [
                            {"id": requested_identifier, "type": UseFunction.copy_of.value}
                        ]
                    }], JSONB)
                ),
            )
        )

        return [
            models.Revision(
                identifier=result.identifier,
                alternate_identifiers=result.alternate_identifiers,
                revision_number=result.revision_number,
                created_at=result.created_at,
                common_metadata=result.common_metadata,
                package_resources=converter.structure(result.package_resources, list[PackageResource])
            )
            for result in self.session.execute(statement).scalars().all()
        ]

    def _fetch_one(self, statement):
        try:
            result = self.session.scalars(statement).one()
            revision = models.Revision(
                identifier=result.identifier,
                alternate_identifiers=result.alternate_identifiers,
                revision_number=result.revision_number,
                created_at=result.created_at,
                common_metadata=result.common_metadata,
                package_resources=converter.structure(result.package_resources, list[PackageResource])
            )
            return revision
        except sqlalchemy.exc.NoResultFound:
            return None

    def get_revisions(self, identifier: str) -> list[models.Revision]:
        statement = select(Revision).where(Revision.identifier == identifier)
        results = self.session.scalars(statement).all()

        revisions = []
        for result in results:
            revisions.append(models.Revision(
                identifier=result.identifier,
                alternate_identifiers=result.alternate_identifiers,
                revision_number=result.revision_number,
                created_at=result.created_at,
                common_metadata=result.common_metadata,
                package_resources=converter.structure(result.package_resources, list[PackageResource])
            ))
        return revisions
