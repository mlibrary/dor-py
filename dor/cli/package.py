from pathlib import Path
from typing import Annotated

import typer


package_app = typer.Typer()


@package_app.command()
def upload(
    packet: Annotated[str, typer.Argument(help="Path to a JSONL packet file.")]
):
    packet_path = Path(packet)
    if not packet_path.exists():
        typer.secho("Packet file was not found at the path provided.", fg=typer.colors.RED)
        raise typer.Exit(1)

    print(packet)
