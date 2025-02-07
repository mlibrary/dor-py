import pytest
import sqlalchemy

from dor.adapters.catalog import SqlalchemyCatalog


@pytest.mark.usefixtures("db_session", "sample_revision")
def test_catalog_adds_revision(db_session, sample_revision) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()

    rows = list(
        db_session.execute(sqlalchemy.text("""
            select *
            from catalog_revision
            where identifier = :identifier
        """), { "identifier": "00000000-0000-0000-0000-000000000001" })
    )
    assert len(rows) == 1
    assert str(rows[0].identifier) == "00000000-0000-0000-0000-000000000001"


@pytest.mark.usefixtures("db_session", "sample_revision")
def test_catalog_gets_revision(db_session, sample_revision) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()

    revision = catalog.get("00000000-0000-0000-0000-000000000001")
    assert revision == sample_revision


@pytest.mark.usefixtures("db_session", "sample_revision")
def test_catalog_gets_by_alternate_identifier(db_session, sample_revision) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()

    revision = catalog.get_by_alternate_identifier("xyzzy:00000001")
    assert revision == sample_revision


@pytest.mark.usefixtures("db_session", "sample_revision")
def test_catalog_returns_none_when_no_alternate_identifier_matches(db_session, sample_revision) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()

    revision = catalog.get_by_alternate_identifier("xyzzy:00000001.404")
    assert revision is None
