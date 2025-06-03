import uuid
from datetime import datetime, UTC
from functools import partial

from pytest_bdd import scenario, given, when, then, parsers

from dor.adapters.converter import converter
from dor.domain.models import Revision
from dor.providers.models import (
    Agent, AlternateIdentifier, FileMetadata, FileReference, PackageResource,
    PreservationEvent, StructMap, StructMapItem, StructMapType
)
from dor.service_layer import catalog_service
from dor.service_layer.unit_of_work import AbstractUnitOfWork


scenario = partial(scenario, './inspect_revision.feature')


@scenario('Revision summary')
def test_revision_summary():
    pass


@scenario('Revision file sets')
def test_revision_file_sets():
    pass


@given(
    parsers.parse(
        u'a preserved monograph with an alternate identifier of "{alt_id}"'),
    target_fixture="revision"
)
def _(alt_id, unit_of_work: AbstractUnitOfWork):
    revision = Revision(
        identifier=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        alternate_identifiers=[alt_id],
        revision_number=1,
        created_at=datetime(2025, 2, 5, 12, 0, 0, 0, tzinfo=UTC),
        common_metadata={
            "@schema": "urn:umich.edu:dor:schema:common",
            "title": "Discussion also Republican owner hot already itself.",
            "author": "Kimberly Garza",
            "publication_date": "1989-04-16",
            "subjects": [
                "Liechtenstein",
                "Vietnam",
            ],
        },
        package_resources=[
            PackageResource(
                id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                type="Monograph",
                root=True,
                alternate_identifiers=[AlternateIdentifier(
                    id="xyzzy:00000001", type="DLXS"
                )],
                events=[
                    PreservationEvent(
                        identifier="abdcb901-721a-4be0-a981-14f514236633",
                        type="ingest",
                        datetime=datetime(2016, 11, 29, 13, 51, 14, tzinfo=UTC),
                        detail="Middle president push visit information feel most.",
                        agent=Agent(
                            address="christopherpayne@example.org",
                            role="collection manager",
                        ),
                    )
                ],
                metadata_files=[
                    FileMetadata(
                        id="_0193d5f0-7f64-7ac8-8f94-85c55c7313e4",
                        use="function:service",
                        ref=FileReference(
                            locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.function:service.json",
                            mdtype="schema:common",
                            mimetype="application/json+schema",
                        ),
                    ),
                    FileMetadata(
                        id="_0193d5f0-7f65-783e-b7b4-485b6f6b24d0",
                        use="function:source",
                        ref=FileReference(
                            locref="00000000-0000-0000-0000-000000000001/metadata/00000000-0000-0000-0000-000000000001.function:source.json",
                            mdtype="schema:monograph",
                            mimetype="application/json+schema",
                        ),
                    ),
                ],
                struct_maps=[
                    StructMap(
                        id="SM1",
                        type=StructMapType.physical,
                        items=[
                            StructMapItem(
                                order=1,
                                type="structure:page",
                                label="Page 1",
                                file_set_id="00000000-0000-0000-0000-000000001001",
                            ),
                            StructMapItem(
                                order=2,
                                type="structure:page",
                                label="Page 2",
                                file_set_id="00000000-0000-0000-0000-000000001002",
                            ),
                        ],
                    )
                ],
            ),
            PackageResource(
                id=uuid.UUID("00000000-0000-0000-0000-000000001001"),
                type="File Set",
                alternate_identifiers=[AlternateIdentifier(
                    id="xyzzy:00000001:00000001", type="DLXS"
                )],
                events=[
                    PreservationEvent(
                        identifier="fe4c76e5-dbf1-4934-97fb-52ef5a68f073",
                        type="generate access derivative",
                        datetime=datetime(1993, 6, 11, 4, 44, 7, tzinfo=UTC),
                        detail="Night wonder three him family structure simple.",
                        agent=Agent(
                            address="arroyoalan@example.net", role="image processing"
                        ),
                    ),
                    PreservationEvent(
                        identifier="3bdcb1e3-4674-4b9c-83c8-4f9f9fe50812",
                        type="extract text",
                        datetime=datetime(1988, 5, 26, 18, 33, 46, tzinfo=UTC),
                        detail="Player center road attorney speak wait partner.",
                        agent=Agent(
                            address="jonathanjones@example.net", role="ocr processing"
                        ),
                    ),
                ],
                metadata_files=[
                    FileMetadata(
                        id="_0193d5f0-7e72-7481-b6fd-0f916c30b396",
                        use="function:technical",
                        ref=FileReference(
                            locref="00000000-0000-0000-0000-000000001001/metadata/00000001.function:source.format:image.jpg.function:technical.mix.xml",
                            mdtype="NISOIMG",
                        ),
                    ),
                    FileMetadata(
                        id="_0193d5f0-7e75-7803-8e41-71323b7b3284",
                        use="function:technical",
                        ref=FileReference(
                            locref="00000000-0000-0000-0000-000000001001/metadata/00000001.function:service.format:image.jpg.function:technical.mix.xml",
                            mdtype="NISOIMG",
                        ),
                    ),
                    FileMetadata(
                        id="_0193d5f0-7f54-7268-b9b1-821085acdcf7",
                        use="function:technical",
                        ref=FileReference(
                            locref="00000000-0000-0000-0000-000000001001/metadata/00000001.function:service.format:text-plain.txt.function:technical.textmd.xml",
                            mdtype="TEXTMD",
                        ),
                    ),
                ],
                data_files=[
                    FileMetadata(
                        id="_be653ff450ae7f3520312a53e56c00bc",
                        mdid="_0193d5f0-7e72-7481-b6fd-0f916c30b396",
                        use="function:source",
                        ref=FileReference(
                            locref="00000000-0000-0000-0000-000000001001/data/00000001.function:source.format:image.jpg",
                            mimetype="image/jpeg",
                        ),
                    ),
                    FileMetadata(
                        id="_7e923d9c33b3859e1327fa53a8e609a1",
                        groupid="_be653ff450ae7f3520312a53e56c00bc",
                        mdid="_0193d5f0-7e75-7803-8e41-71323b7b3284",
                        use="function:service",
                        ref=FileReference(
                            locref="00000000-0000-0000-0000-000000001001/data/00000001.function:service.format:image.jpg",
                            mimetype="image/jpeg",
                        ),
                    ),
                    FileMetadata(
                        id="_764ba9761fbc6cbf0462d28d19356148",
                        groupid="_be653ff450ae7f3520312a53e56c00bc",
                        mdid="_0193d5f0-7f54-7268-b9b1-821085acdcf7",
                        use="function:source",
                        ref=FileReference(
                            locref="00000000-0000-0000-0000-000000001001/data/00000001.function:service.format:text-plain.txt",
                            mimetype="text/plain",
                        ),
                    ),
                ],
            ),
        ],
    )

    with unit_of_work:
        unit_of_work.catalog.add(revision)
        unit_of_work.commit()

    return revision


@when(
    parsers.parse(
        u'the Collection Manager looks up the revision by "{alt_id}"'),
    target_fixture="summary"
)
def _(alt_id, unit_of_work: AbstractUnitOfWork):
    with unit_of_work:
        revision = unit_of_work.catalog.get_by_alternate_identifier(alt_id)
    summary = catalog_service.summarize(revision)
    return summary


@then(u'the Collection Manager sees the summary of the revision.')
def _(revision: Revision, summary):
    expected_summary = dict(
        identifier="00000000-0000-0000-0000-000000000001",
        alternate_identifiers=revision.alternate_identifiers,
        revision_number=1,
        created_at="2025-02-05T12:00:00Z",
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
    parsers.parse(
        u'the Collection Manager lists the contents of the revision for "{alt_id}"'),
    target_fixture="file_sets"
)
def _(alt_id, unit_of_work):
    with unit_of_work:
        revision = unit_of_work.catalog.get_by_alternate_identifier(alt_id)
    file_sets = catalog_service.get_file_sets(revision)
    return file_sets


@then(u'the Collection Manager sees the file sets.')
def _(revision: Revision, file_sets):
    expected_file_sets = [
        converter.unstructure(resource)
        for resource in revision.package_resources if resource.type == 'File Set'
    ]
    assert file_sets == expected_file_sets
