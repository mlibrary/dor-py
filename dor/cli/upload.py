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
    collection: str = typer.Option(..., help="Collection to upload to."),
    profile: str = typer.Option(..., help="Profile to use for the upload."),
):
    asyncio.run(_run_upload(file, folder, name, collection, profile))


async def _run_upload(
    file: List[str],
    folder: str,
    name: str,
    collection: str,
    profile: str,
):
    base_url = config.api_url

    try:
        if not file and not folder:
            raise UploadError("Either 'file' or 'folder' must be provided.", code=400)
        if not name:
            raise UploadError("Name is a required parameter.", code=400)
        if not collection:
            raise UploadError("Collection is a required parameter.", code=400)           
        if not profile:
            raise UploadError("Profile is a required parameter.", code=400)
        # if folder:
        #     if not os.path.exists(folder) or not os.path.isdir(folder):
        #         raise UploadError(f"Folder '{folder}' does not exist or is not a directory.", code=404)
        #     files = [
        #         os.path.join(folder, f)
        #         for f in os.listdir(folder)
        #         if os.path.isfile(os.path.join(folder, f))
        #     ]
        #     if not files:
        #         raise UploadError(f"No files found in folder '{folder}'.", code=404)
        #     file = files
        # if not file:
        #     raise UploadError("No files to upload.", code=404)
  

        async with httpx.AsyncClient(follow_redirects=True) as client:
            result = await run_upload_fileset(
                client,
                base_url,
                file,
                folder=folder,
                name=name,
                collection=collection,
                profile=profile,
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
