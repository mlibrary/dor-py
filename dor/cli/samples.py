import typer
import pathlib

import bagit
from dor.settings import S, ActionChoices

from dor.builders.parts import generate_uuid
from dor.builders.item import build_item

import sys

import re
import codecs
from functools import partial
open_text_file = partial(codecs.open, encoding="utf-8", errors="strict")

app = typer.Typer()

# future? options commented out
@app.command()
def generate(
    collid: str = typer.Option(default=...),
    action: ActionChoices = ActionChoices.store,
    num_scans: int = -1,
    # include_desc: bool = True,
    # include_admin: bool = True,
    # include_structure: bool = True,
    # images: bool = True,
    # texts: bool = True,
    base: int = 0,
    versions: int = 1,
    output_pathname: str = pathlib.Path(__file__).resolve().parent.parent.parent.joinpath("output"),
):

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
    )

    identifier_uuid = generate_uuid(base)
    for version in range(1, versions + 1):
        package_pathname = S.output_pathname.joinpath(
            f"{S.collid}-{identifier_uuid}-v{version}"
        )
        package_pathname.mkdir()
        identifiers = build_item(package_pathname, identifier_uuid, base, version=version)
        bag = bagit.make_bag(package_pathname)

        dor_info = dict([
            ('Action', S.action.value),
            ('Root-Identifier', identifier_uuid),
            ('Identifier', identifiers),
        ])
        with open_text_file(package_pathname / "dor-info.txt", "w") as f:
            for h in dor_info.keys():
                values = dor_info[h]
                if not isinstance(values, list):
                    values = [values]
                for txt in values:
                    # strip CR, LF and CRLF so they don't mess up the tag file
                    txt = re.sub(r"\n|\r|(\r\n)", "", str(txt))
                    f.write("%s: %s\n" % (h, txt))
        bag.save()
        print("...added dor-info.txt")

    print("-30-")
