from unittest import TestCase
from datetime import datetime, UTC
from dor.providers.models import *
from dor.settings import S, template_env

class GeneratePreservationMETSTest(TestCase):
    def setUp(self):
        return super().setUp()

    def test_can_generate_mets(self):
        resources = [
            PackageResource(
                id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
                type="Monograph",
                alternate_identifier=AlternateIdentifier(
                    id="xyzzy:00000001", type="DLXS"
                ),
                events=[
                    PreservationEvent(
                        identifier="e01727d0-b4d9-47a5-925a-4018f9cac6b8",
                        type="ingest",
                        datetime=datetime(1983, 5, 17, 11, 9, 45, tzinfo=UTC),
                        detail="Girl voice lot another blue nearly.",
                        agent=Agent(
                            address="matthew24@example.net", role="collection manager"
                        ),
                    )
                ],
                metadata_files=[
                    FileMetadata(
                        id="_0193972b-e591-7e28-b8cb-1babed52f606",
                        use="DESCRIPTIVE/COMMON",
                        ref=FileReference(
                            locref="../metadata/00000000-0000-0000-0000-000000000001.common.json",
                            mdtype="DOR:SCHEMA",
                            mimetype="application/json",
                        ),
                    ),
                    FileMetadata(
                        id="_0193972b-e592-7647-8e51-10db514433f7",
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
                        identifier="81388465-aefd-4a3d-ba99-a868d062b92e",
                        type="generate access derivative",
                        datetime=datetime(2005, 8, 22, 22, 54, 45, tzinfo=UTC),
                        detail="Method south agree until.",
                        agent=Agent(
                            address="rguzman@example.net", role="image processing"
                        ),
                    ),
                    PreservationEvent(
                        identifier="d53540b9-cd23-4e92-9dff-4b28bf050b26",
                        type="extract text",
                        datetime=datetime(2006, 8, 23, 16, 21, 57, tzinfo=UTC),
                        detail="Hear thus part probably that.",
                        agent=Agent(
                            address="kurt16@example.org", role="ocr processing"
                        ),
                    ),
                ],
                metadata_files=[
                    FileMetadata(
                        id="_0193972b-e4a4-7985-abe2-f3f1259b78ec",
                        use="TECHNICAL",
                        ref=FileReference(
                            locref="../metadata/00000001.source.jpg.mix.xml",
                            mdtype="NISOIMG",
                        ),
                    ),
                    FileMetadata(
                        id="_0193972b-e4ae-73eb-848d-5f8893b68253",
                        use="TECHNICAL",
                        ref=FileReference(
                            locref="../metadata/00000001.access.jpg.mix.xml",
                            mdtype="NISOIMG",
                        ),
                    ),
                    FileMetadata(
                        id="_0193972b-e572-7107-b69c-e2f4c660a9aa",
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
                        mdid="_0193972b-e4a4-7985-abe2-f3f1259b78ec",
                        use="SOURCE",
                        ref=FileReference(
                            locref="../data/00000001.source.jpg",
                            mimetype="image/jpeg",
                        ),
                    ),
                    FileMetadata(
                        id="_7e923d9c33b3859e1327fa53a8e609a1",
                        groupid="_be653ff450ae7f3520312a53e56c00bc",
                        mdid="_0193972b-e4ae-73eb-848d-5f8893b68253",
                        use="ACCESS",
                        ref=FileReference(
                            locref="../data/00000001.access.jpg",
                            mimetype="image/jpeg",
                        ),
                    ),
                    FileMetadata(
                        id="_764ba9761fbc6cbf0462d28d19356148",
                        groupid="_be653ff450ae7f3520312a53e56c00bc",
                        mdid="_0193972b-e572-7107-b69c-e2f4c660a9aa",
                        use="SOURCE",
                        ref=FileReference(
                            locref="../data/00000001.plaintext.txt",
                            mimetype="text/plain",
                        ),
                    ),
                ],
            ),
            PackageResource(
                id=uuid.UUID("00000000-0000-0000-0000-000000001002"),
                type="Asset",
                alternate_identifier=AlternateIdentifier(
                    id="xyzzy:00000001:00000002", type="DLXS"
                ),
                events=[
                    PreservationEvent(
                        identifier="d4bcce33-db4e-413e-98f9-6abd3d83f924",
                        type="generate access derivative",
                        datetime=datetime(1985, 8, 11, 15, 46, 43, tzinfo=UTC),
                        detail="Entire serve message mother.",
                        agent=Agent(
                            address="james98@example.com", role="image processing"
                        ),
                    ),
                    PreservationEvent(
                        identifier="18301575-d6ff-445b-a8f8-deeb3b522866",
                        type="extract text",
                        datetime=datetime(1980, 7, 2, 15, 53, 41, tzinfo=UTC),
                        detail="Way interest unit maybe professional worker.",
                        agent=Agent(
                            address="mary49@example.org", role="ocr processing"
                        ),
                    ),
                ],
                metadata_files=[
                    FileMetadata(
                        id="_0193972b-e57c-79e2-b4fa-6390302aff2f",
                        use="TECHNICAL",
                        ref=FileReference(
                            locref="../metadata/00000002.source.jpg.mix.xml",
                            mdtype="NISOIMG",
                        ),
                    ),
                    FileMetadata(
                        id="_0193972b-e585-7332-b314-c73d875ac900",
                        use="TECHNICAL",
                        ref=FileReference(
                            locref="../metadata/00000002.access.jpg.mix.xml",
                            mdtype="NISOIMG",
                        ),
                    ),
                    FileMetadata(
                        id="_0193972b-e58a-7fa4-8453-3b80c5b563d6",
                        use="TECHNICAL",
                        ref=FileReference(
                            locref="../metadata/00000002.plaintext.txt.textmd.xml",
                            mdtype="TEXTMD",
                        ),
                    ),
                ],
                data_files=[
                    FileMetadata(
                        id="_f442339a2731f043f72460c64ad66fee",
                        mdid="_0193972b-e57c-79e2-b4fa-6390302aff2f",
                        use="SOURCE",
                        ref=FileReference(
                            locref="../data/00000002.source.jpg",
                            mimetype="image/jpeg",
                        ),
                    ),
                    FileMetadata(
                        id="_1cc90346d5f1fe485fc8a3c55d10e753",
                        groupid="_f442339a2731f043f72460c64ad66fee",
                        mdid="_0193972b-e585-7332-b314-c73d875ac900",
                        use="ACCESS",
                        ref=FileReference(
                            locref="../data/00000002.access.jpg",
                            mimetype="image/jpeg",
                        ),
                    ),
                    FileMetadata(
                        id="_59472df4b090349a7440a32ca575f87e",
                        groupid="_f442339a2731f043f72460c64ad66fee",
                        mdid="_0193972b-e58a-7fa4-8453-3b80c5b563d6",
                        use="SOURCE",
                        ref=FileReference(
                            locref="../data/00000002.plaintext.txt",
                            mimetype="text/plain",
                        ),
                    ),
                ],
            ),
        ]

        asset_map = {}
        for resource in resources:
            if resource.type == "Asset":
                identifier = f"urn:dor:{resource.id}"
                asset_map[identifier] = f"{resource.id}.mets2.xml"

        entity_template = template_env.get_template("preservation_mets.xml")
        for resource in resources:
            xmldata = entity_template.render(
                resource=resource,
                asset_map=asset_map,
                action="stored",
                create_date=datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            )

            print(xmldata)
            # break
