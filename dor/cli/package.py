import asyncio
from pathlib import Path
from typing import Annotated

import httpx
import rich
import typer

from dor.config import config
from dor.cli.client.package_client import (
    DepositGroup,
    PackageUploadError,
    upload_packages
)


package_app = typer.Typer()


@package_app.command()
def upload(
    packet: Annotated[str, typer.Argument(help="Path to a JSONL packet file.")]
):
    packet_path = Path(packet)
    if not packet_path.exists():
        typer.echo("Packet file was not found at the path provided.", err=True)
        raise typer.Exit(1)

    deposit_group = DepositGroup.generate()
    typer.echo(
        "Deposit Group\n"
        f"- Identifier: {deposit_group.identifier}\n"
        f"- Date: {deposit_group.date.isoformat()}"
    )

    httpx_client = httpx.AsyncClient(base_url=config.api_url + "/api/v1/")

    result = asyncio.run(upload_packages(
        packet_path=packet_path,
        httpx_client=httpx_client,
        deposit_group=deposit_group
    ))

    typer.echo(f"Successfully submitted metadata for {len(result.response_datas)} package(s).")
    rich.print(result.response_datas)

    for exception in result.exceptions:
        if isinstance(exception, PackageUploadError):
            typer.echo(
                f"Error occurred for package {exception.package_identifier}. " +
                f"Message: {exception.message}",
                err=True
            )
        else:
            typer.echo(f"Unknown exception occurred: {exception}", err=True)
    if result.exceptions:
        raise typer.Exit(1)
