import pytest
import sqlalchemy

from dor.adapters.catalog import SqlalchemyCatalog


@pytest.mark.usefixtures("db_session", "sample_version")
def test_catalog_adds_version(db_session, sample_version) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_version)
        db_session.commit()

    rows = list(
        db_session.execute(sqlalchemy.text("""
            select *
            from catalog_version
            where identifier = :identifier
        """), { "identifier": "00000000-0000-0000-0000-000000000001" })
    )
    assert len(rows) == 1
    assert str(rows[0].identifier) == "00000000-0000-0000-0000-000000000001"


@pytest.mark.usefixtures("db_session", "sample_version")
def test_catalog_gets_version(db_session, sample_version) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_version)
        db_session.commit()

    version = catalog.get("00000000-0000-0000-0000-000000000001")
    assert version == sample_version


@pytest.mark.usefixtures("db_session", "sample_version")
def test_catalog_gets_by_alternate_identifier(db_session, sample_version) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_version)
        db_session.commit()

    version = catalog.get_by_alternate_identifier("xyzzy:00000001")
    assert version == sample_version


@pytest.mark.usefixtures("db_session", "sample_version")
def test_catalog_returns_none_when_no_alternate_identifier_matches(db_session, sample_version) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_version)
        db_session.commit()

    version = catalog.get_by_alternate_identifier("xyzzy:00000001.404")
    assert version is None
