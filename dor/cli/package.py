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
    get_package_metadata_records,
    upload_package
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

    response_datas = []
    exceptions = []
    for package_metadata in get_package_metadata_records(packet_path):
        try:
            result = asyncio.run(upload_package(
                client=httpx_client,
                deposit_group=deposit_group,
                package_metadata=package_metadata
            ))
            response_datas.append(result)
        except Exception as exception:
            exceptions.append(exception)

    typer.echo(f"Successfully submitted metadata for {len(response_datas)} package(s).")
    rich.print(response_datas)

    for exception in exceptions:
        if isinstance(exception, PackageUploadError):
            typer.echo(
                f"Error occurred for package {exception.package_identifier}. " +
                f"Message: {exception.message}",
                err=True
            )
        else:
            typer.echo(f"Unknown exception occurred: {exception}", err=True)
    if exceptions:
        raise typer.Exit(1)
