from faker import Faker
from faker_biology.taxonomy import ModelOrganism


from datetime import datetime, UTC
import json
import random

from dor.settings import S, template_env
from .parts import Md, MdGrp, File, FileGrp, calculate_checksum, make_paths
from .file_set import build_file_set
from .premis import build_event

def build_resource(package_pathname, resource_identifier, version=1):
    resource_pathname = make_paths(package_pathname.joinpath(str(resource_identifier)))

    alternate_identifier = resource_identifier.alternate_identifier

    resource_template = template_env.get_template("mets_resource.xml")
    premis_event_template = template_env.get_template("premis_event.xml")
    premis_object_template = template_env.get_template("premis_object.xml")

    file_set_identifiers = []
    num_scans = random.randint(1, 10) if S.num_scans < 0 else S.num_scans
    sequences = range(1, num_scans + 1)
    if version > 1:
        sequences = random.sample(
            sequences, random.randint(1, min(len(sequences) - 1, 2)))

    for seq in sequences:
        identifier = build_file_set(resource_identifier, seq, package_pathname, version)
        file_set_identifiers.append(identifier)

    if version > 1:
        resource_pathname.joinpath("descriptor", resource_identifier + ".mets2.xml").open(
            "w"
        ).write(
            resource_template.render(
                file_set_identifiers=file_set_identifiers,
                object_identifier=resource_identifier,
                action=S.action.value,
                create_date=datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                version=version,
                event=build_event(event_type='update', linking_agent_type='collection manager'),
            )
        )
        return resource_identifier

    if S.seed > -1: Faker.seed(S.seed)
    fake = Faker(locale=["it_IT", "en_US", "ja_JP"])
    fake["en_US"].add_provider(ModelOrganism)

    mdsec_items = []

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

    metadata_pathname = resource_pathname.joinpath(
        "metadata", resource_identifier + ".metadata.json"
    )
    metadata_pathname.open("w").write(json.dumps(metadata, indent=4))

    metadata = {
        "@schema": "urn:umich.edu:dor:schema:common",
        "title": metadata["title"],
        "author": metadata["author"],
        "publication_date": metadata["publication_date"],
        "subjects": metadata["places"] + metadata["identification"],
    }
    common_pathname = resource_pathname.joinpath(
        "metadata", resource_identifier + ".common.json"
    )
    common_pathname.open("w").write(json.dumps(metadata, indent=4))

    mdsec_items.append(
        Md(
            use="DESCRIPTIVE/COMMON",
            mdtype="DOR:SCHEMA",
            locref=f"{resource_identifier}/metadata/{resource_identifier}.common.json",
            checksum=calculate_checksum(common_pathname),
            mimetype="application/json",
        )
    )

    mdsec_items.append(
        Md(
            use="DESCRIPTIVE",
            mdtype="DOR:SCHEMA",
            locref=f"{resource_identifier}/metadata/{resource_identifier}.metadata.json",
            checksum=calculate_checksum(metadata_pathname),
            mimetype="application/json",
        )
    )

    resource_pathname.joinpath(
        "metadata", resource_identifier + ".premis.object.xml"
    ).open("w").write(
        premis_object_template.render(
            alternate_identifier=alternate_identifier,
            scans_count=len(file_set_identifiers),
            collid=S.collid,
            seed=S.seed if S.seed > -1 else False,
        )
    )
    mdsec_items.append(
        Md(
            use="PROVENANCE",
            mdtype="PREMIS",
            locref=f"{resource_identifier}/metadata/{resource_identifier}.premis.object.xml",
            mimetype="text/xml"
        )
    )

    premis_event = build_event(event_type="ingest", linking_agent_type="collection manager")
    resource_pathname.joinpath("metadata", resource_identifier + ".premis.event.xml").open("w").write(
        premis_event_template.render(
            event=premis_event
        )
    )
    mdsec_items.append(
        Md(
            use="PROVENANCE",
            mdtype="PREMIS",
            locref=f"{resource_identifier}/metadata/{resource_identifier}.premis.event.xml",
            mimetype="text/xml"
        )
    )

    resource_pathname.joinpath(
        "descriptor", resource_identifier + ".monograph.mets2.xml"
    ).open("w").write(
        resource_template.render(
            file_set_identifiers=file_set_identifiers,
            object_identifier=resource_identifier,
            alternate_identifier=alternate_identifier,
            mdsec_items=mdsec_items,
            create_date=datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            version=version,
            collid=S.collid,
            premis_event=premis_event,
        )
    )

    return [resource_identifier, *file_set_identifiers]
