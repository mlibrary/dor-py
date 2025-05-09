import typer
from typing import List
import httpx
import os

app = typer.Typer()


@app.command()
def upload(
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
    upload_files = []

    if folder:
        if not os.path.exists(folder) or not os.path.isdir(folder):
            typer.echo(
                f"Error: Folder '{folder}' does not exist or is not a directory.",
                err=True,
            )
            raise typer.Exit(code=1)

        files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if os.path.isfile(os.path.join(folder, f))
        ]
        if not files:
            typer.echo(f"Error: No files found in folder '{folder}'.", err=True)
            raise typer.Exit(code=1)

        typer.echo(
            f"Uploading {len(files)} files from folder '{folder}' to collection '{collection}' with profile '{profile}'."
        )

        # Prepare files for upload
        for file_path in files:
            upload_files.append(
                (
                    "files",
                    (
                        os.path.basename(file_path),
                        open(file_path, "rb"),
                        "application/octet-stream",
                    ),
                )
            )

    elif file:
        for file_path in file:
            if not os.path.exists(file_path):
                typer.echo(f"Error: File '{file_path}' does not exist.", err=True)
                raise typer.Exit(code=1)

            typer.echo(
                f"Uploading file '{file_path}' to collection '{collection}' with profile '{profile}'."
            )

            # Prepare single file for upload
            upload_files.append(
                (
                    "files",
                    (
                        os.path.basename(file_path),
                        open(file_path, "rb"),
                        "application/octet-stream",
                    ),
                )
            )

    else:
        typer.echo("Error: Either --file or --folder must be specified.", err=True)
        raise typer.Exit(code=1)

    # Prepare data payload
    data = {
        "name": name,
        "collection": collection,
        "profile": profile,
    }

    try:
        # Send POST request to the API
        response = httpx.post(
            "http://0.0.0.0:8000/api/v1/filesets/",
            files=upload_files,
            data=data,
        )
        response.raise_for_status()  # Raise exception for HTTP errors

        # Handle successful response
        result = response.json()
        typer.echo(f"Fileset created successfully: {result}")

    except httpx.RequestError as exc:
        typer.echo(f"An error occurred while making the request: {exc}", err=True)
        raise typer.Exit(1)

    except httpx.HTTPStatusError as exc:
        typer.echo(
            f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}",
            err=True,
        )
        raise typer.Exit(1)

    finally:
        # Ensure all file streams are closed
        for _, (_, file, _) in upload_files:
            file.close()
