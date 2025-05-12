import pytest
import sqlalchemy

from dor.adapters.catalog import MemoryCatalog, SqlalchemyCatalog


# MemoryCatalog

@pytest.mark.usefixtures("sample_revision")
def test_memory_catalog_adds_revision(sample_revision) -> None:
    catalog = MemoryCatalog()
    catalog.add(sample_revision)

    assert len(catalog.revisions) == 1
    assert catalog.revisions[0] == sample_revision


@pytest.mark.usefixtures("sample_revision")
def test_memory_catalog_gets_revision(sample_revision) -> None:
    catalog = MemoryCatalog()
    catalog.add(sample_revision)

    revision = catalog.get("00000000-0000-0000-0000-000000000001")
    assert revision == sample_revision


@pytest.mark.usefixtures("sample_revision", "sample_revision_two")
def test_memory_catalog_returns_latest_revision(sample_revision, sample_revision_two) -> None:
    catalog = MemoryCatalog()
    catalog.add(sample_revision)
    catalog.add(sample_revision_two)

    revision = catalog.get("00000000-0000-0000-0000-000000000001")
    assert revision == sample_revision_two


@pytest.mark.usefixtures("sample_revision")
def test_memory_catalog_gets_by_alternate_identifier(sample_revision) -> None:
    catalog = MemoryCatalog()
    catalog.add(sample_revision)

    revision = catalog.get_by_alternate_identifier("xyzzy:00000001")
    assert revision == sample_revision


@pytest.mark.usefixtures("sample_revision", "sample_revision_two")
def test_memory_catalog_returns_latest_for_alternate_identifier(
    sample_revision, sample_revision_two
) -> None:
    catalog = MemoryCatalog()
    catalog.add(sample_revision)
    catalog.add(sample_revision_two)

    revision = catalog.get_by_alternate_identifier("xyzzy:00000001")
    assert revision == sample_revision_two


@pytest.mark.usefixtures("sample_revision", "referenced_revision")
def test_memory_catalog_returns_latest_by_file_set_identifier(
    sample_revision, referenced_revision
) -> None:
    catalog = MemoryCatalog()
    catalog.add(sample_revision)
    catalog.add(referenced_revision)

    revisions = catalog.find_by_file_set("00000000-0000-0000-0000-000000001001")
    assert sample_revision in revisions
    assert referenced_revision in revisions


@pytest.mark.usefixtures("sample_revision", "sample_revision_two")
def test_memory_catalog_gets_revisions(
    sample_revision, sample_revision_two
) -> None:
    catalog = MemoryCatalog()
    catalog.add(sample_revision)
    catalog.add(sample_revision_two)

    revisions = catalog.get_revisions("00000000-0000-0000-0000-000000000001")
    assert revisions == [sample_revision, sample_revision_two]


# SqlalchemyCatalog

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
        """), {"identifier": "00000000-0000-0000-0000-000000000001"})
    )
    assert len(rows) == 1
    assert str(rows[0].identifier) == "00000000-0000-0000-0000-000000000001"
    assert rows[0].revision_number == 1

    rows = list(
        db_session.execute(sqlalchemy.text("""
            select *
            from catalog_current_revision
            where identifier = :identifier
        """), {"identifier": "00000000-0000-0000-0000-000000000001"})
    )
    assert len(rows) == 1
    assert str(rows[0].identifier) == "00000000-0000-0000-0000-000000000001"
    assert rows[0].revision_number == 1


@pytest.mark.usefixtures("db_session", "sample_revision", "sample_revision_two")
def test_catalog_accumulates_revision_and_updates_current_revision(
    db_session, sample_revision, sample_revision_two
) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()

    with db_session.begin():
        catalog.add(sample_revision_two)
        db_session.commit()

    rows = list(
        db_session.execute(sqlalchemy.text("""
            select *
            from catalog_revision
            where identifier = :identifier
        """), {"identifier": "00000000-0000-0000-0000-000000000001"})
    )
    assert len(rows) == 2

    rows = list(
        db_session.execute(sqlalchemy.text("""
            select *
            from catalog_current_revision
            where identifier = :identifier
        """), {"identifier": "00000000-0000-0000-0000-000000000001"})
    )
    assert len(rows) == 1
    assert str(rows[0].identifier) == "00000000-0000-0000-0000-000000000001"
    assert rows[0].revision_number == 2
    assert rows[0].common_metadata == sample_revision_two.common_metadata


@pytest.mark.usefixtures("db_session", "sample_revision")
def test_catalog_gets_revision(db_session, sample_revision) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()

    revision = catalog.get("00000000-0000-0000-0000-000000000001")
    assert revision == sample_revision


@pytest.mark.usefixtures("db_session", "sample_revision", "sample_revision_two")
def test_catalog_returns_latest_revision(
    db_session, sample_revision, sample_revision_two
) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()

    with db_session.begin():
        catalog.add(sample_revision_two)
        db_session.commit()

    revision = catalog.get("00000000-0000-0000-0000-000000000001")
    assert revision == sample_revision_two


@pytest.mark.usefixtures("db_session", "sample_revision")
def test_catalog_gets_by_alternate_identifier(db_session, sample_revision) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()

    revision = catalog.get_by_alternate_identifier("xyzzy:00000001")
    assert revision == sample_revision


@pytest.mark.usefixtures("db_session", "sample_revision", "sample_revision_two")
def test_catalog_returns_latest_for_alternate_identifier(
    db_session, sample_revision, sample_revision_two
) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()

    with db_session.begin():
        catalog.add(sample_revision_two)
        db_session.commit()

    revision = catalog.get_by_alternate_identifier("xyzzy:00000001")
    assert revision == sample_revision_two


@pytest.mark.usefixtures("db_session", "sample_revision")
def test_catalog_returns_none_when_no_alternate_identifier_matches(db_session, sample_revision) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()

    revision = catalog.get_by_alternate_identifier("xyzzy:00000001.404")
    assert revision is None


@pytest.mark.usefixtures("db_session", "sample_revision", "referenced_revision")
def test_catalog_returns_latest_for_alternate_identifier(
    db_session, sample_revision, referenced_revision
) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()

    with db_session.begin():
        catalog.add(referenced_revision)
        db_session.commit()

    revisions = catalog.find_by_file_set("00000000-0000-0000-0000-000000001001")

    assert sample_revision in revisions
    assert referenced_revision in revisions


@pytest.mark.usefixtures("db_session", "sample_revision", "sample_revision_two")
def test_catalog_gets_revisions(
    db_session, sample_revision, sample_revision_two
) -> None:
    catalog = SqlalchemyCatalog(db_session)
    with db_session.begin():
        catalog.add(sample_revision)
        db_session.commit()

    with db_session.begin():
        catalog.add(sample_revision_two)
        db_session.commit()

    revisions = catalog.get_revisions("00000000-0000-0000-0000-000000000001")
    assert revisions == [sample_revision, sample_revision_two]


@pytest.mark.usefixtures("db_session")
def test_catalog_returns_empty_array_when_no_revisions_exist(db_session) -> None:
    catalog = SqlalchemyCatalog(db_session)

    revisions = catalog.get_revisions("40400000-0000-0000-0000-000000000001")
    assert revisions == []
