import typer
import pathlib

import bagit
from dor.settings import S, ActionChoices

from dor.builders.parts import generate_uuid, Identifier, get_faker, reset_fakers, get_datetime
from dor.builders.resource import build_resource

import sys
import datetime

app = typer.Typer()

"""
## About the Sample Generator

Submission packages are a bag representing a single root digital object, 
containing its required assets, e.g. a monograph and its scanned pages.
This group of objects represents a preservation goal: everything about the 
monograph that should be preserved and described.

By default, UUIDs are created from a starting integer to make them 
easier to scan/read when generated (e.g. 00000000-0000-0000-0000-000000000001).

## What's in the package?

The submission package is your standard BagIt bag, with the addition of
a "dor-info.txt" tag file containing proposed fields that are still 
under discussion. The "Identifier" key is multi-valued and is the list of
all objects in this package; there's a future scenario where the monograph-type
object will _refer_ to assets not preserved under its repository item. 
The "Root-Identifier" key points to that monograph-type object.

## What's in the METS?

Some XPaths:

* `//METS:mets/@OBJID` returns the object identifier
* `//METS:mets/METS:metsHdr/@TYPE` returns the "internal resource type" of the object
* `//METS:mets/METS:metsHdr/METS:altRecordID[@TYPE="DLXS"]` returns the alternate identifier
* `//METS:mets//PREMIS:event[PREMIS:eventType="ingest"]` returns the commit details

In the structMap of the monograph:

```
<METS:div ORDERLABEL="5" TYPE="page" ORDER="5" LABEL="Page 5" ID="urn:dor:00000000-0000-0000-0000-000000001005">
```

The `ID` is the asset identifier: the `urn:dor:` prefix satisfies XML IDs constraints.

"""

@app.command()
def generate(
    collid: str = typer.Option(default="xyzzy", help="collection id"),
    deposit_group: str = typer.Option(default=None, help="deposit group identifier"),
    action: ActionChoices = typer.Option(default=ActionChoices.store, help="what should ingest do with this package?"),
    num_scans: int = typer.Option(default=-1, help="number of page scans; -1 == random number"),
    start: int = typer.Option(default=1, help="seed number for the root identifier"),
    versions: int = typer.Option(default=1, help="number of versions to generate"),
    partial: bool = typer.Option(default=True, help="assume partial updates"),
    output_pathname: str = pathlib.Path(__file__).resolve().parent.parent.parent.joinpath("output"),
    seed: int = typer.Option(default=-1, help="Faker seed value"),
):

    """
    Generate a sample submission package.
    """

    S.update(
        collid=collid,
        action=action,
        num_scans=num_scans,
        # include_desc=include_desc,
        # include_admin=include_admin,
        # include_structure=include_structure,
        # images=images,
        # texts=texts,
        output_pathname=output_pathname,
        seed=seed,
    )

    if S.seed > -1:
        print("-- generating with seed", seed)

    resource_identifier = Identifier(start=start, collid=collid)
    for version in range(1, versions + 1):

        # reset Faker to ensure every version is similar
        reset_fakers()
        fake = get_faker()

        if deposit_group is None:
            version_deposit_group = fake.uuid4()
        else:
            version_deposit_group = deposit_group

        deposit_group_date = fake.get_datetime(f"+{version}w")

        package_pathname = S.output_pathname.joinpath(
            f"{S.collid}-{resource_identifier}-v{version}"
        )
        package_pathname.mkdir()
        identifiers = build_resource(package_pathname, resource_identifier, version=version, partial=partial)
        bag = bagit.make_bag(package_pathname)

        # one time ugly
        dor_info = dict([
            ('Action', S.action.value),
            ('Deposit-Group-Identifier', deposit_group),
            ('Deposit-Group-Date', deposit_group_date),
            ('Root-Identifier', str(resource_identifier)),
            ('Identifier', identifiers),
        ])
        bagit._make_tag_file(package_pathname / "dor-info.txt", dor_info)
        bag.save()

    print("-30-")
