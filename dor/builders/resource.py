from faker import Faker
from faker_biology.taxonomy import ModelOrganism


from datetime import datetime, UTC
import json
import random

from dor.settings import S, template_env
from .parts import (
    Md,
    MdGrp,
    File,
    FileGrp,
    IdGenerator,
    UseFunctions,
    StructureTypes,
    calculate_checksum,
    make_paths,
    get_faker,
    get_datetime,
    flatten_use,
    F,
    FMD,
)
from .file_set import build_file_set
from .premis import build_event


def build_resource(package_pathname, resource_identifier, version=1, partial=True):
    resource_pathname = make_paths(package_pathname.joinpath(str(resource_identifier)))

    alternate_identifier = resource_identifier.alternate_identifier

    fake = get_faker(role="resource")

    resource_template = template_env.get_template("mets_resource.xml")
    premis_event_template = template_env.get_template("premis_event.xml")
    premis_object_template = template_env.get_template("premis_object.xml")

    generate_md_identifier = IdGenerator(resource_identifier)

    file_set_identifiers = []
    num_scans = random.randint(1, 10) if S.num_scans < 0 else S.num_scans
    sequences = range(1, num_scans + 1)
    if version > 1 and partial:
        sequences = random.sample(
            sequences, random.randint(1, min(len(sequences) - 1, 2))
        )

    for seq in sequences:
        identifier = build_file_set(resource_identifier, seq, package_pathname, version)
        file_set_identifiers.append(identifier)

    if version > 1 and partial:

        mdsec_items = []
        premis_event = build_event(
            event_type="ingest", linking_agent_type="collection manager"
        )
        resource_pathname.joinpath(
            "metadata", f"{resource_identifier}-{version}.premis.event.xml"
        ).open("w").write(premis_event_template.render(event=premis_event))
        mdsec_items.append(
            Md(
                id=generate_md_identifier(),
                use=flatten_use(UseFunctions.event),
                mdtype="PREMIS",
                locref=f"{resource_identifier}/metadata/{resource_identifier}-{version}.premis.event.xml",
                mimetype="text/xml",
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
                create_date=fake.get_datetime(),
                version=version,
                event=premis_event,
            )
        )
        return resource_identifier

    mdsec_items = []

    metadata_fake = get_faker("metadata")
    metadata_fake["en_US"].add_provider(ModelOrganism)

    metadata = {}
    metadata["@schema"] = f"urn:umich.edu:dor:schema:{S.collid}"
    metadata["title"] = metadata_fake["en_US"].sentence()
    metadata["author"] = metadata_fake["en_US"].name()
    metadata["author_ja"] = metadata_fake["ja_JP"].name()
    metadata["description"] = metadata_fake["en_US"].paragraph(5)
    metadata["description_ja"] = metadata_fake["ja_JP"].paragraph(5)
    metadata["publication_date"] = metadata_fake["en_US"].date()
    metadata["places"] = [metadata_fake.country() for _ in range(5)]
    metadata["identification"] = [
        metadata_fake["en_US"].organism_latin() for _ in range(5)
    ]

    metadata_filename = FMD(
        resource_identifier,
        resource_identifier,
        [UseFunctions.source],
        "application/json+schema",
    )

    # metadata_pathname = resource_pathname.joinpath(
    #     "metadata", resource_identifier + ".metadata.json"
    # )
    metadata_pathname = resource_pathname / metadata_filename.path
    metadata_pathname.open("w").write(json.dumps(metadata, indent=4))

    metadata = {
        "@schema": "urn:umich.edu:dor:schema:common",
        "title": metadata["title"],
        "author": metadata["author"],
        "publication_date": metadata["publication_date"],
        "subjects": metadata["places"] + metadata["identification"],
    }

    common_filename = FMD(
        resource_identifier,
        resource_identifier,
        [UseFunctions.service],
        "application/json+schema",
    )

    common_pathname = resource_pathname / common_filename.path
    common_pathname.open("w").write(json.dumps(metadata, indent=4))

    mdsec_items.append(
        Md(
            id=generate_md_identifier(),
            use=flatten_use(UseFunctions.service),
            mdtype=common_filename.mdtype,
            locref=common_filename.locref,
            checksum=calculate_checksum(common_pathname),
            mimetype=common_filename.mimetype,
        )
    )

    mdsec_items.append(
        Md(
            id=generate_md_identifier(),
            use=flatten_use(UseFunctions.source),
            mdtype=metadata_filename.mdtype,
            locref=metadata_filename.locref,
            checksum=calculate_checksum(metadata_pathname),
            mimetype=metadata_filename.mimetype,
        )
    )

    premis_filename = FMD(
        resource_identifier,
        resource_identifier,
        [UseFunctions.provenance],
        "text/xml+premis",
    )
    (resource_pathname / premis_filename.path).open("w").write(
        premis_object_template.render(
            alternate_identifier=alternate_identifier,
            scans_count=len(file_set_identifiers),
            collid=S.collid,
            seed=S.seed if S.seed > -1 else False,
        )
    )
    mdsec_items.append(
        Md(
            id=generate_md_identifier(),
            use=flatten_use(UseFunctions.provenance),
            mdtype=premis_filename.mdtype,
            locref=premis_filename.locref,
            mimetype=premis_filename.mimetype,
        )
    )

    premis_event = build_event(
        event_type="ingest", linking_agent_type="collection manager"
    )

    premis_filename = FMD(
        resource_identifier,
        resource_identifier,
        [UseFunctions.event],
        "text/xml+premis",
    )
    (resource_pathname / premis_filename.path).open("w").write(
        premis_event_template.render(event=premis_event)
    )
    mdsec_items.append(
        Md(
            id=generate_md_identifier(),
            use=flatten_use(UseFunctions.event),
            mdtype=premis_filename.mdtype,
            locref=premis_filename.locref,
            mimetype=premis_filename.mimetype,
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
            create_date=get_datetime(),
            version=version,
            collid=S.collid,
            premis_event=premis_event,
        )
    )

    return [resource_identifier, *file_set_identifiers]
