import asyncio
from pathlib import Path
from typing import Annotated

import httpx
import rich
import typer

from dor.cli.client.upload_client import (
    generate_profiles,
    run_upload_fileset_with_limit,
    UploadError
)
from dor.config import config


upload_app = typer.Typer()


@upload_app.command(name = "upload")
def run_upload(
    folder: Annotated[str, typer.Argument(help="Path to a folder containing files to upload.")],
    project_id: str = typer.Option(..., help="Collection to upload to."),
    image: list[str] = typer.Option(default_factory=list, help="image processing"),
    text: list[str] = typer.Option(default_factory=list, help="text processing"),
):
    asyncio.run(_run_upload(folder, project_id, image,text))


async def _run_upload(
    folder: str,
    project_id: str,
    image: list[str],
    text: list[str],
):
    base_url = config.api_url
    type_profiles: dict[str, list[str]] = {}
    
    if image:
        type_profiles["image"] = image
    if text:
        type_profiles["text"] = text
    if not type_profiles:
        typer.echo("No profiles provided. Use --image or --text to specify profiles.")
        raise typer.Exit(1)

    profiles = generate_profiles(folder_path=Path(folder), type_profiles=type_profiles)
    fileset_profiles: dict[str, dict[str, list[str]]] = {}
    for file_name in profiles:
        name = Path(file_name).stem
        if name not in fileset_profiles:
            fileset_profiles[name] = {}
        fileset_profiles[name][file_name] = profiles[file_name]

    semaphore = asyncio.Semaphore(10)

    async with httpx.AsyncClient(follow_redirects=True) as client:
        tasks = []
        for name in fileset_profiles:
            tasks.append(run_upload_fileset_with_limit(
                sempahore=semaphore,
                client=client,
                base_url=base_url,
                project_id=project_id,
                name=name,
                profiles=fileset_profiles[name],
                folder=folder,
            ))
        results = await asyncio.gather(*tasks, return_exceptions=True)

    data_results = []
    exceptions = []
    for result in results:
        if isinstance(result, BaseException):
            exceptions.append(result)
        else:
            data_results.append(result)

    typer.echo(f"Successfully submitted {len(data_results)} fileset(s) for creation.")
    rich.print(data_results)

    for exception in exceptions:
        if isinstance(exception, UploadError):
            typer.secho(f"Upload error: {exception}", fg="white", bg="red", bold=True, err=True)
            typer.echo(f"Details: {exception.message}, Code: {exception.code}", err=True)
        elif isinstance(exception, httpx.RequestError):
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
