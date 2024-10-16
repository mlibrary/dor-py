import typer
import pathlib

import bagit
from dor.settings import S, ActionChoices

from dor.builders.parts import generate_uuid
from dor.builders.item import build_item

import sys

app = typer.Typer()

@app.command()
def generate(
    collid: str,
    action: ActionChoices = ActionChoices.store,
    num_scans: int = -1,
    include_desc: bool = True,
    include_admin: bool = True,
    include_structure: bool = True,
    images: bool = True,
    texts: bool = True,
    total: int = 1,
    versions: int = 1,
    output_pathname: str = pathlib.Path(__file__).resolve().parent.parent.parent.joinpath("output"),
):
    
    S.update(
        collid=collid,
        action=action,
        num_scans=num_scans,
        include_desc=include_desc,
        include_admin=include_admin,
        include_structure=include_structure,
        images=images,
        texts=texts,
        total=total,
        output_pathname=output_pathname,
    )

    package_uuid = generate_uuid()
    for version in range(1, versions + 1):
        package_pathname = S.output_pathname.joinpath(
            f"{S.collid}-{package_uuid}-v{version}"
        )
        package_pathname.mkdir()
        for _ in range(S.total):
            build_item(package_pathname, version=version)
            bagit.make_bag(package_pathname)

    print("-30-")
