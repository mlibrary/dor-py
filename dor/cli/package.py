from typing import Annotated

import typer


package_app = typer.Typer()


@package_app.command()
def upload(
    packet: Annotated[str, typer.Argument(help="Path to a JSONL packet file.")]
):
    print(packet)
