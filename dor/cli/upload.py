import asyncio
import typer
import httpx
import os

from dor.cli.client.upload_client import UploadError, run_upload_fileset
from dor.config import config

from typing import List

upload_app = typer.Typer()


@upload_app.command(name = "run")
def run_upload(
    file: List[str] = typer.Option(
        None, help="Paths to files to upload. Can be specified multiple times."
    ),
    folder: str = typer.Option(
        None, help="Path to a folder containing files to upload."
    ),
    name: str = typer.Option(..., help="Name of the file or fileset."),
    project_id: str = typer.Option(..., help="Collection to upload to."),
    commands: str = typer.Option(..., help="Profile to use for the upload."),
):
    asyncio.run(_run_upload(file, folder, name, project_id, commands))


async def _run_upload(
    file: List[str],
    folder: str,
    name: str,
    project_id: str,
    commands: str,
):
    base_url = config.api_url

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            result = await run_upload_fileset(
                client,
                base_url,
                file,
                folder=folder,
                name=name,
                project_id=project_id,
                commands=commands,
            )
        typer.echo(f"Fileset created successfully: {result}")

    except UploadError as exc:
        typer.secho(f"Upload error: {exc}", fg="white", bg="red", bold=True)
        typer.echo(f"Details: {exc.message}, Code: {exc.code}", err=True)
        raise typer.Exit(1)

    except httpx.RequestError as exc:
        typer.echo(f"An error occurred while making the request: {exc}", err=True)
        raise typer.Exit(1)

    except httpx.HTTPStatusError as exc:
        typer.echo(
            f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}",
            err=True,
        )
        raise typer.Exit(1)
