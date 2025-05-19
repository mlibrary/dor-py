import asyncio
from email.policy import default
from pathlib import Path
import typer
import httpx
import os

from dor.cli.client.upload_client import UploadError, generate_profiles, run_upload_fileset
from dor.config import config

from typing import List

upload_app = typer.Typer()


@upload_app.command(name = "upload")
def run_upload(
    # file: List[str] = typer.Option(
    #     None, help="Paths to files to upload. Can be specified multiple times."
    # ),
    folder: str = typer.Option(
        None, help="Path to a folder containing files to upload."
    ),
    # name: str = typer.Option(..., help="Name of the file or fileset."),
    project_id: str = typer.Option(..., help="Collection to upload to."),
    image: List[str] = typer.Option(default_factory=list, help="image processing"),
    text: List[str] = typer.Option(default_factory=list, help="text processing"),
    # commands: str = typer.Option(..., help="Profile to use for the upload."),
):
    asyncio.run(_run_upload(folder, project_id, image,text))


async def _run_upload(
    folder: str,
    project_id: str,
    image: list[str],
    text: list[str],
):
    base_url = config.api_url
    type_profiles: dict[str, List[str]] = {}
    if image:
        type_profiles["image"] = image
    if text:
        type_profiles["text"] = text
    profiles = generate_profiles(folder_path=Path(folder), type_profiles=type_profiles)
    fileset_profiles: dict[str,dict] = {}
    for file_name in profiles:
        name = Path(file_name).stem
        if name not in fileset_profiles:
            fileset_profiles[name] = {}    
        fileset_profiles[name][file_name] = profiles[file_name]    
    for name in fileset_profiles:             
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                result = await run_upload_fileset(
                    client,
                    base_url,
                    profiles=fileset_profiles[name],
                    folder=folder,
                    name=name,
                    project_id=project_id,                   
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
