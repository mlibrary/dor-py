import os
import uuid

import pytest
import sqlalchemy

from dor.adapters.catalog import mapper_registry, SqlalchemyCatalog, start_mappers
from dor.domain.models import Bin


def setup_module() -> None:
    start_mappers()


@pytest.fixture
def engine() -> sqlalchemy.Engine:
    engine_url = sqlalchemy.engine.URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host=os.environ["POSTGRES_HOST"],
        database="dor_test"
    )
    engine = sqlalchemy.create_engine(engine_url, echo=True)
    return engine


@pytest.fixture
def db_session(engine: sqlalchemy.Engine) -> sqlalchemy.orm.Session:
    mapper_registry.metadata.drop_all(engine)
    mapper_registry.metadata.create_all(engine)
    return sqlalchemy.orm.Session(engine)


@pytest.fixture
def sample_bin() -> Bin:
    return Bin(
        identifier=uuid.UUID("00000000-0000-0000-0000-000000000001"), 
        alternate_identifiers=["xyzzy:00000001"], 
        common_metadata={
            "@schema": "urn:umich.edu:dor:schema:common",
            "title": "Discussion also Republican owner hot already itself.",
            "author": "Kimberly Garza",
            "publication_date": "1989-04-16",
            "subjects": [
                "Liechtenstein",
                "Vietnam",
                "San Bartolomeo",
                "Bangladesh",
                "Liberia",
                "Mus musculus",
                "Schizosaccharomyces pombe",
                "Caenorhabditis elegans",
                "Drosophila melanogaster",
                "Xenopus laevis"
            ]
        }
    ) 


def test_catalog_adds_bin(db_session, sample_bin) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session:
        catalog.add(sample_bin)
        db_session.commit()

    rows = list(
        db_session.execute(sqlalchemy.text("""
            select *
            from catalog_bin
            where identifier = :identifier
        """), { "identifier": "00000000-0000-0000-0000-000000000001" })
    )
    assert len(rows) == 1
    assert str(rows[0].identifier) == "00000000-0000-0000-0000-000000000001"


def test_catalog_gets_bin(db_session, sample_bin) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session:
        catalog.add(sample_bin)
        db_session.commit()

        bin = catalog.get("00000000-0000-0000-0000-000000000001")

    assert bin is not None
    expected_bin = Bin(
        identifier=uuid.UUID("00000000-0000-0000-0000-000000000001"), 
        alternate_identifiers=["xyzzy:00000001"], 
        common_metadata={
            "@schema": "urn:umich.edu:dor:schema:common",
            "title": "Discussion also Republican owner hot already itself.",
            "author": "Kimberly Garza",
            "publication_date": "1989-04-16",
            "subjects": [
                "Liechtenstein",
                "Vietnam",
                "San Bartolomeo",
                "Bangladesh",
                "Liberia",
                "Mus musculus",
                "Schizosaccharomyces pombe",
                "Caenorhabditis elegans",
                "Drosophila melanogaster",
                "Xenopus laevis"
            ]
        }
    ) 


    assert bin == expected_bin
