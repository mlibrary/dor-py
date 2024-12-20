from faker import Faker
from faker_biology.taxonomy import ModelOrganism


from datetime import datetime, UTC
import json
import random

from dor.settings import S, template_env
from .parts import Md, MdGrp, File, FileGrp, calculate_checksum, generate_ulid
from .asset import build_asset
from .premis import build_event

def build_item(package_pathname, item_identifier, version=1):
    item_pathname = package_pathname.joinpath(str(item_identifier))
    item_pathname.mkdir()

    alternate_identifier = item_identifier.alternate_identifier

    for d in ["data", "descriptor", "metadata"]:
        d_pathname = item_pathname.joinpath(d)
        d_pathname.mkdir()

    item_template = template_env.get_template("mets_item.xml")

    asset_identifiers = []
    num_scans = random.randint(1, 10) if S.num_scans < 0 else S.num_scans
    sequences = range(1, num_scans + 1)
    if version > 1:
        sequences = random.sample(
            sequences, random.randint(1, min(len(sequences) - 1, 2)))

    for seq in sequences:
        identifier = build_asset(item_identifier, seq, item_pathname, version)
        asset_identifiers.append(identifier)

    if version > 1:
        item_pathname.joinpath("descriptor", item_identifier + ".mets2.xml").open(
            "w"
        ).write(
            item_template.render(
                asset_identifiers=asset_identifiers,
                object_identifier=item_identifier,
                action=S.action.value,
                create_date=datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                version=version,
                event=build_event(event_type='update', linking_agent_type='collection manager'),
            )
        )
        return object_identifier

    fake = Faker(locale=["it_IT", "en_US", "ja_JP"])
    fake["en_US"].add_provider(ModelOrganism)
    metadata = {}
    metadata["@schema"] = f"urn:umich.edu:dor:schema:{S.collid}"
    metadata["title"] = fake["en_US"].sentence()
    metadata["author"] = fake["en_US"].name()
    metadata["author_ja"] = fake["ja_JP"].name()
    metadata["description"] = fake["en_US"].paragraph(5)
    metadata["description_ja"] = fake["ja_JP"].paragraph(5)
    metadata["publication_date"] = fake["en_US"].date()
    metadata["places"] = [fake.country() for _ in range(5)]
    metadata["identification"] = [fake["en_US"].organism_latin() for _ in range(5)]

    metadata_pathname = item_pathname.joinpath(
        "metadata", item_identifier + ".metadata.json"
    )
    metadata_pathname.open("w").write(json.dumps(metadata, indent=4))

    metadata = {
        "@schema": "urn:umich.edu:dor:schema:common",
        "title": metadata["title"],
        "author": metadata["author"],
        "publication_date": metadata["publication_date"],
        "subjects": metadata["places"] + metadata["identification"],
    }
    common_pathname = item_pathname.joinpath(
        "metadata", item_identifier + ".common.json"
    )
    common_pathname.open("w").write(json.dumps(metadata, indent=4))

    desc_group = MdGrp(use="DESCRIPTIVE")
    desc_group.items.append(
        Md(
            use="DESCRIPTIVE/COMMON",
            mdtype="DOR:SCHEMA",
            locref=f"../metadata/{item_identifier}.common.json",
            checksum=calculate_checksum(common_pathname),
        )
    )

    desc_group.items.append(
        Md(
            use="DESCRIPTIVE",
            mdtype="DOR:SCHEMA",
            locref=f"../metadata/{item_identifier}.metadata.json",
            checksum=calculate_checksum(metadata_pathname),
        )
    )

    item_pathname.joinpath("descriptor", item_identifier + ".monograph.mets2.xml").open(
        "w"
    ).write(
        item_template.render(
            asset_identifiers=asset_identifiers,
            object_identifier=item_identifier,
            alternate_identifier=alternate_identifier,
            desc_group=desc_group,
            action=S.action.value,
            create_date=datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            version=version,
            collid=S.collid,
            event=build_event(
                event_type="ingest", linking_agent_type="collection manager"
            ),
        )
    )

    return [item_identifier, *asset_identifiers]
