import asyncio
from pathlib import Path
from typing import Annotated

import httpx
import rich
import typer

from dor.config import config
from dor.cli.client.package_client import (
    create_deposit_group,
    get_package_metadatas,
    upload_packages
)


package_app = typer.Typer()


@package_app.command()
def upload(
    packet: Annotated[str, typer.Argument(help="Path to a JSONL packet file.")]
):
    packet_path = Path(packet)
    if not packet_path.exists():
        typer.echo("Packet file was not found at the path provided.")
        raise typer.Exit(1)

    deposit_group = create_deposit_group()
    typer.echo(
        "Deposit Group\n"
        f"  Identifier: {deposit_group.identifier}\n"
        f"  Date: {deposit_group.date.isoformat()}"
    )

    package_metadatas = get_package_metadatas(packet_path)
    typer.echo(f"{len(package_metadatas)} package(s) to be uploaded.")

    httpx_client = httpx.AsyncClient(base_url=config.api_url + "/api/v1/")

    results = asyncio.run(upload_packages(
        client=httpx_client,
        deposit_group=deposit_group,
        package_metadatas=package_metadatas
    ))

    data_results = []
    exceptions = []
    for result in results:
        if isinstance(result, BaseException):
            exceptions.append(result)
        else:
            data_results.append(result)

    typer.echo(f"Successfully submitted {len(data_results)} packages(s) for creation.")
    rich.print(data_results)

    for exception in exceptions:
        if isinstance(exception, httpx.RequestError):
            typer.echo(f"An error occurred while making a request: {exception}", err=True)
        elif isinstance(exception, httpx.HTTPStatusError):
            typer.echo(
                f"HTTP error occurred: {exception.response.status_code} - {exception.response.text}",
                err=True
            )
        else:
            typer.echo(f"Unknown exception occurred: {exception}", err=True)
    if exceptions:
        raise typer.Exit(1)
