import uuid
from datetime import datetime, UTC
from functools import partial

import pytest
from pydantic_core import to_jsonable_python
from pytest_bdd import scenario, given, when, then, parsers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dor.adapters.catalog import Base, _custom_json_serializer
from dor.config import config
from dor.domain.models import Bin
from dor.providers.models import (
    Agent, AlternateIdentifier, FileMetadata, FileReference, PackageResource,
    PreservationEvent, StructMap, StructMapItem, StructMapType
)
from dor.service_layer import catalog_service
from dor.service_layer.unit_of_work import AbstractUnitOfWork, SqlalchemyUnitOfWork
from gateway.fake_repository_gateway import FakeRepositoryGateway

scenario = partial(scenario, '../inspect_bin.feature')

@scenario('Revision summary')
def test_revision_summary():
    pass

@scenario('Revision file sets')
def test_revision_file_sets():
    pass

@pytest.fixture
def unit_of_work() -> AbstractUnitOfWork:
    engine = create_engine(
        config.get_test_database_engine_url(), json_serializer=_custom_json_serializer
    )
    session_factory = sessionmaker(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    uow = SqlalchemyUnitOfWork(gateway=FakeRepositoryGateway(), session_factory=session_factory)
    return uow

@given(
    parsers.parse(u'a preserved monograph with an alternate identifier of "{alt_id}"'),
    target_fixture="bin"
)
def _(alt_id, unit_of_work: AbstractUnitOfWork):
    bin = Bin(
        identifier=uuid.UUID("00000000-0000-0000-0000-000000000001"), 
        alternate_identifiers=[alt_id],
        common_metadata={
            "@schema": "urn:umich.edu:dor:schema:common",
            "title": "Discussion also Republican owner hot already itself.",
            "author": "Kimberly Garza",
            "publication_date": "1989-04-16",
            "subjects": [
                "Liechtenstein",
                "Vietnam",
            ]
        },
        package_resources=[
            PackageResource(
                id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                type="Monograph",
                alternate_identifier=AlternateIdentifier(id="xyzzy:00000001", type="DLXS"),
                events=[
                    PreservationEvent(
                        identifier="abdcb901-721a-4be0-a981-14f514236633",
                        type="ingest",
                        datetime=datetime(2016, 11, 29, 13, 51, 14, tzinfo=UTC),
                        detail="Middle president push visit information feel most.",
                        agent=Agent(
                            address="christopherpayne@example.org", role="collection manager"
                        ),
                    )
                ],
                metadata_files=[
                    FileMetadata(
                        id="_0193d5f0-7f64-7ac8-8f94-85c55c7313e4",
                        use="DESCRIPTIVE/COMMON",
                        ref=FileReference(
                            locref="../metadata/00000000-0000-0000-0000-000000000001.common.json",
                            mdtype="DOR:SCHEMA",
                            mimetype="application/json",
                        ),
                    ),
                    FileMetadata(
                        id="_0193d5f0-7f65-783e-b7b4-485b6f6b24d0",
                        use="DESCRIPTIVE",
                        ref=FileReference(
                            locref="../metadata/00000000-0000-0000-0000-000000000001.metadata.json",
                            mdtype="DOR:SCHEMA",
                            mimetype="application/json",
                        ),
                    ),
                    FileMetadata(
                        id="RIGHTS1",
                        use="RIGHTS",
                        ref=FileReference(
                            locref="https://creativecommons.org/publicdomain/zero/1.0/",
                            mdtype="OTHER",
                        ),
                    ),
                ],
                struct_maps=[
                    StructMap(
                        id="SM1",
                        type=StructMapType.PHYSICAL,
                        items=[
                            StructMapItem(
                                order=1,
                                type="page",
                                label="Page 1",
                                asset_id="urn:dor:00000000-0000-0000-0000-000000001001",
                            ),
                            StructMapItem(
                                order=2,
                                type="page",
                                label="Page 2",
                                asset_id="urn:dor:00000000-0000-0000-0000-000000001002",
                            ),
                        ],
                    )
                ],
            ),
            PackageResource(
                id=uuid.UUID("00000000-0000-0000-0000-000000001001"),
                type="Asset",
                alternate_identifier=AlternateIdentifier(
                    id="xyzzy:00000001:00000001", type="DLXS"
                ),
                events=[
                    PreservationEvent(
                        identifier="fe4c76e5-dbf1-4934-97fb-52ef5a68f073",
                        type="generate access derivative",
                        datetime=datetime(1993, 6, 11, 4, 44, 7, tzinfo=UTC),
                        detail="Night wonder three him family structure simple.",
                        agent=Agent(address="arroyoalan@example.net", role="image processing"),
                    ),
                    PreservationEvent(
                        identifier="3bdcb1e3-4674-4b9c-83c8-4f9f9fe50812",
                        type="extract text",
                        datetime=datetime(1988, 5, 26, 18, 33, 46, tzinfo=UTC),
                        detail="Player center road attorney speak wait partner.",
                        agent=Agent(address="jonathanjones@example.net", role="ocr processing"),
                    ),
                ],
                metadata_files=[
                    FileMetadata(
                        id="_0193d5f0-7e72-7481-b6fd-0f916c30b396",
                        use="TECHNICAL",
                        ref=FileReference(
                            locref="../metadata/00000001.source.jpg.mix.xml",
                            mdtype="NISOIMG",
                        ),
                    ),
                    FileMetadata(
                        id="_0193d5f0-7e75-7803-8e41-71323b7b3284",
                        use="TECHNICAL",
                        ref=FileReference(
                            locref="../metadata/00000001.access.jpg.mix.xml",
                            mdtype="NISOIMG",
                        ),
                    ),
                    FileMetadata(
                        id="_0193d5f0-7f54-7268-b9b1-821085acdcf7",
                        use="TECHNICAL",
                        ref=FileReference(
                            locref="../metadata/00000001.plaintext.txt.textmd.xml",
                            mdtype="TEXTMD",
                        ),
                    ),
                ],
                data_files=[
                    FileMetadata(
                        id="_be653ff450ae7f3520312a53e56c00bc",
                        mdid="_0193d5f0-7e72-7481-b6fd-0f916c30b396",
                        use="SOURCE",
                        ref=FileReference(
                            locref="../data/00000001.source.jpg",
                            mimetype="image/jpeg",
                        ),
                    ),
                    FileMetadata(
                        id="_7e923d9c33b3859e1327fa53a8e609a1",
                        groupid="_be653ff450ae7f3520312a53e56c00bc",
                        mdid="_0193d5f0-7e75-7803-8e41-71323b7b3284",
                        use="ACCESS",
                        ref=FileReference(
                            locref="../data/00000001.access.jpg",
                            mimetype="image/jpeg",
                        ),
                    ),
                    FileMetadata(
                        id="_764ba9761fbc6cbf0462d28d19356148",
                        groupid="_be653ff450ae7f3520312a53e56c00bc",
                        mdid="_0193d5f0-7f54-7268-b9b1-821085acdcf7",
                        use="SOURCE",
                        ref=FileReference(
                            locref="../data/00000001.plaintext.txt",
                            mimetype="text/plain",
                        ),
                    ),
                ],
            )
        ]
    )

    with unit_of_work:
        unit_of_work.catalog.add(bin)
        unit_of_work.commit()

    return bin

@when(
    parsers.parse(u'the Collection Manager looks up the bin by "{alt_id}"'),
    target_fixture="summary"
)
def _(alt_id, unit_of_work: AbstractUnitOfWork):
    with unit_of_work:
        bin = unit_of_work.catalog.get_by_alternate_identifier(alt_id)
    summary = catalog_service.summarize(bin)
    return summary

@then(u'the Collection Manager sees the summary of the bin')
def _(bin: Bin, summary):
    expected_summary = dict(
        identifier="00000000-0000-0000-0000-000000000001", 
        alternate_identifiers=bin.alternate_identifiers,
        common_metadata={
            "@schema": "urn:umich.edu:dor:schema:common",
            "title": "Discussion also Republican owner hot already itself.",
            "author": "Kimberly Garza",
            "publication_date": "1989-04-16",
            "subjects": [
                "Liechtenstein",
                "Vietnam",
            ]
        }
    )
    assert summary == expected_summary

@when(
    parsers.parse(u'the Collection Manager lists the contents of the bin for "{alt_id}"'),
    target_fixture="file_sets"
)
def _(alt_id, unit_of_work):
    with unit_of_work:
        bin = unit_of_work.catalog.get_by_alternate_identifier(alt_id)
    file_sets = catalog_service.get_file_sets(bin)
    return file_sets

@then(u'the Collection Manager sees the file sets.')
def _(bin: Bin, file_sets):
    expected_file_sets = [
        to_jsonable_python(resource) 
        for resource in bin.package_resources if resource.type == 'Asset'
    ]
    assert file_sets == expected_file_sets

