import typer
from typing import List
import pathlib

import random
import sys
from typing import List
import uuid
from uuid import uuid4
from datetime import datetime
import hashlib

from faker import Faker

from dor.config import config
import sqlalchemy.exc
from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, LargeBinary, UniqueConstraint, func, select, String, Uuid
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship

from rich.console import Console
from rich.table import Table

from dor.adapters.converter import converter
from dor.adapters.sqlalchemy import Base

def create_uuid_from_string(val: str):
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return uuid.UUID(hex=hex_string)

### models
### adapted from https://github.com/APTrust/registry/blob/master/db/schema.sql

class IntellectualObject(Base):
    __tablename__ = "aptrustish_intellectual_object"
    id: Mapped[int] = mapped_column(primary_key=True)
    bin_identifier: Mapped[uuid.UUID] = mapped_column(Uuid, unique=False, index=True)
    identifier: Mapped[uuid.UUID] = mapped_column(Uuid, unique=False, index=True)
    alternate_identifiers: Mapped[list] = Column(MutableList.as_mutable(ARRAY(String)))
    type: Mapped[str] = mapped_column(String)
    revision_number: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    title: Mapped[str] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)

    file_set_files: Mapped[List["FileSetFile"]] = relationship(back_populates="intellectual_object")
    premis_events: Mapped[List["PremisEvent"]] = relationship(back_populates="intellectual_object")
    revision: Mapped["LatestRevision"] = relationship(back_populates="intellectual_object", uselist=False)

    __table_args__ = (
        UniqueConstraint('identifier', 'revision_number', name='uq_intellectual_object_revision'),
    )

# identifier = file path in bag
class FileSetFile(Base):
    __tablename__ = "aptrustish_file_set_file"
    id: Mapped[int] = mapped_column(primary_key=True)
    identifier: Mapped[str] = mapped_column(String)
    # identifier: Mapped[uuid.UUID] = mapped_column(Uuid, unique=True)
    file_format: Mapped[str] = mapped_column(String)
    size: Mapped[int] = mapped_column(Integer)
    digest: Mapped[bytes] = mapped_column(LargeBinary(32), unique=False, nullable=False)
    revision_number: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_fixity_check: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    intellectual_object_id: Mapped[int] = mapped_column(ForeignKey("aptrustish_intellectual_object.id"), index=True)

    intellectual_object: Mapped["IntellectualObject"] = relationship(back_populates="file_set_files")
    premis_events: Mapped[List["PremisEvent"]] = relationship(back_populates="file_set_file")
    checksums: Mapped[List["Checksum"]] = relationship(back_populates="file_set_file")


class PremisEvent(Base):
    __tablename__ = "aptrustish_premis_event"
    id: Mapped[int] = mapped_column(primary_key=True)
    # event_identifier
    identifier: Mapped[uuid.UUID] = mapped_column(Uuid, unique=True)
    type: Mapped[str] = mapped_column(String)
    detail: Mapped[str] = mapped_column(String, nullable=True)
    outcome: Mapped[str] = mapped_column(String, nullable=True)
    outcome_detail_note: Mapped[str] = mapped_column(String, nullable=True)
    linking_agent: Mapped[str] = mapped_column(String, nullable=True)
    linking_agent_role: Mapped[list] = Column(MutableList.as_mutable(ARRAY(String)))
    # foreign key to file set file    
    intellectual_object_id: Mapped[int] = mapped_column(ForeignKey("aptrustish_intellectual_object.id"), nullable=True, index=True)
    file_set_file_id: Mapped[int] = mapped_column(ForeignKey("aptrustish_file_set_file.id"), nullable=True, index=True)

    intellectual_object: Mapped["IntellectualObject"] = relationship(back_populates="premis_events")
    file_set_file: Mapped["FileSetFile"] = relationship(back_populates="premis_events")


class Checksum(Base):
    __tablename__ = "aptrustish_checksum"
    id: Mapped[int] = mapped_column(primary_key=True)
    algorithm: Mapped[str] = mapped_column(String)
    # xdatetime: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    digest: Mapped[bytes] = mapped_column(LargeBinary(32), unique=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    file_set_file_id: Mapped[int] = mapped_column(ForeignKey("aptrustish_file_set_file.id"), nullable=False, index=True)

    file_set_file: Mapped["FileSetFile"] = relationship(back_populates="checksums")


# because CurrentRevision is taken
class LatestRevision(Base):
    __tablename__ = "aptrustish_latest_revision"
    id: Mapped[int] = mapped_column(primary_key=True)
    revision_number: Mapped[int] = mapped_column(Integer)
    intellectual_object_identifier: Mapped[uuid.UUID] = mapped_column(Uuid, unique=True, index=True)
    intellectual_object_id: Mapped[int] = mapped_column(ForeignKey("aptrustish_intellectual_object.id"), unique=False, nullable=True)

    intellectual_object: Mapped["IntellectualObject"] = relationship(back_populates="revision")


# database connections made here to avoid the existing tables
engine_url = config.get_database_engine_url()
engine = sqlalchemy.create_engine(engine_url, echo=False)

connection = engine.connect()
session = sqlalchemy.orm.Session(bind=connection)

def seed_objects(num_objects: int=100):

    fake = Faker()
    
    i = session.query(func.count(IntellectualObject.id)).join(LatestRevision).scalar()

    intellectual_objects = []
    while i < num_objects:
        num_scans = random.randint(1, 5)
        sequences = range(1, num_scans + 1)

        bin_alternate_identifier = f"xyzzy:f{i+1:08d}"
        bin_identifier = create_uuid_from_string(bin_alternate_identifier)

        intellectual_object = IntellectualObject(
            identifier=bin_identifier,
            bin_identifier=bin_identifier,
            alternate_identifiers=[bin_alternate_identifier],
            type=random.choice(["type:monograph", "type:serial_issue", "type:newspaper_issue", "type:album", "type:artifact"]),
            revision_number=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            title=fake.catch_phrase(),
            description=fake.paragraph(nb_sentences=1),
        )
        session.add(intellectual_object)

        for file_identifier in [
                f"descriptor/{bin_identifier}.mets2.xml", 
                f"metadata/{bin_identifier}.function:source.xml",
                f"metadata/{bin_identifier}.function:service.xml"
            ]:
            digest = fake.sha256(raw_output=True)
            file_set_file = FileSetFile(
                identifier=file_identifier,
                file_format="application/xml",
                size=fake.random_int(min=600),
                digest=digest,
                revision_number=1,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                last_fixity_check=datetime.now()
            )

            intellectual_object.file_set_files.append(file_set_file)

            event = PremisEvent(
                identifier=fake.uuid4(),
                type="ingestion start",
            )
            file_set_file.premis_events.append(event)
            intellectual_object.premis_events.append(event)

            checksum = Checksum(
                algorithm="sha256",
                digest=digest,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            checksum.file_set_file = file_set_file
            session.add(checksum)

        event = PremisEvent(
            identifier=fake.uuid4(),
            type="accession ",
        )
        intellectual_object.premis_events.append(event)

        # now just the intellectual object
        revision = LatestRevision(
            revision_number=intellectual_object.revision_number,
            intellectual_object=intellectual_object,
            intellectual_object_identifier=intellectual_object.identifier
        )
        session.add(revision)
        session.commit()

        for seq in sequences:
            alternate_identifier = f"{bin_alternate_identifier}:{seq:08d}"
            intellectual_object = IntellectualObject(
                identifier=create_uuid_from_string(alternate_identifier),
                bin_identifier=bin_identifier,
                alternate_identifiers=[alternate_identifier],
                type="type:fileset",
                revision_number=1,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            session.add(intellectual_object)

            num_files = random.randint(3, 9)
            for fid in range(num_files):
                digest = fake.sha256(raw_output=True)
                file_set_file = FileSetFile(
                    identifier=fake.file_path(),
                    file_format=fake.mime_type(),
                    size=fake.random_int(min=600),
                    digest=digest,
                    revision_number=1,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    last_fixity_check=datetime.now()
                )

                intellectual_object.file_set_files.append(file_set_file)

                event = PremisEvent(
                    identifier=fake.uuid4(),
                    type="ingestion start",
                )
                file_set_file.premis_events.append(event)
                intellectual_object.premis_events.append(event)

                checksum = Checksum(
                    algorithm="sha256",
                    digest=digest,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                checksum.file_set_file = file_set_file
                session.add(checksum)

            event = PremisEvent(
                identifier=fake.uuid4(),
                type="accession ",
            )
            intellectual_object.premis_events.append(event)

            # now just the intellectual object
            revision = LatestRevision(
                revision_number=intellectual_object.revision_number,
                intellectual_object=intellectual_object,
                intellectual_object_identifier=intellectual_object.identifier
            )
            session.add(revision)            

            session.commit()
            intellectual_objects.append(intellectual_object.id)
            print("--", i, intellectual_object.alternate_identifiers[0])

        i += 1

    # randomly make some revisions
    current_revisions = {}
    last_revision = {}
    versioned = random.choices(intellectual_objects, k=1_000)
    for intellectual_object_id in versioned:
        revision = current_revisions.setdefault(intellectual_object_id, 1)
        next_revision = revision + 1
        current_revisions[intellectual_object_id] = next_revision

        # this will always be selecting version 1, but who's counting?
        intellectual_object = session.execute(select(IntellectualObject).filter_by(id=intellectual_object_id)).scalar_one()

        next_intellectual_object = IntellectualObject(
            bin_identifier=intellectual_object.bin_identifier,
            identifier=intellectual_object.identifier,
            alternate_identifiers=intellectual_object.alternate_identifiers,
            type="type:fileset",
            revision_number=next_revision,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        session.add(next_intellectual_object)

        for file_set_file in intellectual_object.file_set_files:
            digest = fake.sha256(raw_output=True)
            next_file_set_file = FileSetFile(
                identifier=file_set_file.identifier,
                file_format=file_set_file.file_format,
                size=fake.random_int(min=600),
                digest=digest,
                revision_number=next_revision,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                last_fixity_check=datetime.now()
            )

            next_intellectual_object.file_set_files.append(next_file_set_file)

            event = PremisEvent(
                identifier=fake.uuid4(),
                type="ingestion start",
            )
            next_file_set_file.premis_events.append(event)
            next_intellectual_object.premis_events.append(event)

            checksum = Checksum(
                algorithm="sha256",
                digest=digest,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            checksum.file_set_file = next_file_set_file
            session.add(checksum)

        event = PremisEvent(
            identifier=fake.uuid4(),
            type="accession ",
        )
        next_intellectual_object.premis_events.append(event)

        # now update the revision
        if intellectual_object_id in last_revision:
            revision = session.execute(select(LatestRevision).filter_by(id=last_revision[intellectual_object_id])).scalar_one()
        else:
            revision = intellectual_object.revision

        if revision is None:
            print(intellectual_object.id, next_revision)
        revision.intellectual_object = next_intellectual_object
        revision.revision_number = next_revision
        session.add(revision)

        session.commit()

        last_revision[intellectual_object_id] = revision.id
        print("∆", next_intellectual_object.alternate_identifiers[0], next_intellectual_object.revision_number)


aptrust_app = typer.Typer()

@aptrust_app.command()
def initialize(num_objects: int=100):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    seed_objects(num_objects)

@aptrust_app.command()
def seed(num_objects: int=100):
    seed_objects(num_objects)

@aptrust_app.command()
def objects():
    possible_identifiers = session.execute(select(LatestRevision.intellectual_object_identifier)).all()
    random.shuffle(possible_identifiers)

    table = Table(title="Intellectual Objects")
    table.add_column("bin", no_wrap=True)
    table.add_column("identifier", no_wrap=True)
    table.add_column("alternate_identifiers", no_wrap=False)
    table.add_column("type", no_wrap=True)
    table.add_column("num_fileset_files", no_wrap=True)
    table.add_column("revision_number", no_wrap=True)
    table.add_column("created_at", no_wrap=True)
    table.add_column("updated_at", no_wrap=True)
    table.add_column("title", no_wrap=True)

    for identifier in random.sample(possible_identifiers, 100):

        identifier = identifier[0]
        intellectual_object = session.execute(select(IntellectualObject).join(LatestRevision).filter_by(intellectual_object_identifier=identifier)).scalar_one()
        table.add_row(
            str(intellectual_object.bin_identifier),
            str(intellectual_object.identifier),
            "; ".join(intellectual_object.alternate_identifiers),
            intellectual_object.type,
            str(len(intellectual_object.file_set_files)),
            str(intellectual_object.revision_number),
            intellectual_object.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            intellectual_object.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            intellectual_object.title
        )
        # for file_set_file in intellectual_object.file_set_files:
        #     print("--", file_set_file.id, file_set_file.identifier)

    console = Console()
    console.print(table)


@aptrust_app.command()
def files():
    file_set_select = select(FileSetFile).join(LatestRevision, LatestRevision.intellectual_object_id == FileSetFile.intellectual_object_id)

    table = Table(title="File Set Files")
    table.add_column("identifier", no_wrap=True)
    table.add_column("file_format", no_wrap=True)
    table.add_column("size", no_wrap=True)
    table.add_column("revision_number", no_wrap=True)
    table.add_column("created_at", no_wrap=True)
    table.add_column("updated_at", no_wrap=True)
    table.add_column("last_fixity_check", no_wrap=True)

    for file_set_file in session.execute(file_set_select).scalars():
        table.add_row(
            file_set_file.identifier,
            file_set_file.file_format,
            str(file_set_file.size),
            str(file_set_file.revision_number),
            file_set_file.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            file_set_file.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            file_set_file.last_fixity_check.strftime("%Y-%m-%d %H:%M:%S"),
        )
    
    console = Console()
    console.print(table)

