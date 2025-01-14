import pytest
import sqlalchemy

from dor.adapters.catalog import SqlalchemyCatalog


@pytest.mark.usefixtures("db_session", "sample_bin")
def test_catalog_adds_bin(db_session, sample_bin) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
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


@pytest.mark.usefixtures("db_session", "sample_bin")
def test_catalog_gets_bin(db_session, sample_bin) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_bin)
        db_session.commit()

    bin = catalog.get("00000000-0000-0000-0000-000000000001")
    assert bin == sample_bin


@pytest.mark.usefixtures("db_session", "sample_bin")
def test_catalog_gets_by_alternate_identifier(db_session, sample_bin) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_bin)
        db_session.commit()

    bin = catalog.get_by_alternate_identifier("xyzzy:00000001")
    assert bin == sample_bin


@pytest.mark.usefixtures("db_session", "sample_bin")
def test_catalog_returns_none_when_no_alternate_identifier_matches(db_session, sample_bin) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_bin)
        db_session.commit()

    bin = catalog.get_by_alternate_identifier("xyzzy:00000001.404")
    assert bin is None
