import asyncio
import json
import os
import mimetypes
from pathlib import Path
from typing import Any, Optional, Tuple

import httpx


class UploadError(Exception):
    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self):
        if self.code:
            return f"[Error {self.code}] {self.message}"
        return self.message


async def run_upload_fileset(
    client: httpx.AsyncClient,
    base_url: str,
    project_id: str,
    name: str,
    profiles: dict[str, list[str]],
    folder: str,
) -> dict[str, Any]:
    """Upload fileset with dynamic profile-based commands."""
    upload_files = []
    try:

        if not os.path.exists(folder) or not os.path.isdir(folder):
            raise UploadError(
                f"Folder '{folder}' does not exist or is not a directory.", code=404
            )
        file_paths = [
            Path(folder) / file_name for file_name in profiles.keys()
        ]    

        upload_files = prepare_files_form_param(file_paths)

        params = {
            "name": name,
            "project_id": project_id,
            "file_profiles": json.dumps(profiles),  # Serialize profiles to JSON
        }

        response = await client.post(f"{base_url}/api/v1/filesets", files=upload_files, data=params)
        response.raise_for_status()
        return response.json()
    finally:
        # Ensure all file streams are closed
        for _, (_, upload_file_fh) in upload_files:
            upload_file_fh.close()


async def run_upload_fileset_with_limit(
    sempahore: asyncio.Semaphore,
    client: httpx.AsyncClient,
    base_url: str,
    project_id: str,
    name: str,
    profiles: dict[str, list[str]],
    folder: str,
) -> dict[str, Any]:
    async with sempahore:
        result = await run_upload_fileset(
            client=client,
            base_url=base_url,
            project_id=project_id,
            name=name,
            profiles=profiles,
            folder=folder
        )
    return result


def prepare_files_form_param(file_paths: list[Path]) -> list[Tuple[str, Tuple[str, Any]]]:
    upload_files: list[Tuple[str, Tuple[str, Any]]] = []
    for file_path in file_paths:
        if not file_path.exists():
            raise UploadError(f"File '{file_path}' does not exist.", code=404)
        upload_files.append(
            (
                "files",
                (
                    file_path.name,
                    open(file_path, "rb"),
                ),
            )
        )
    return upload_files


def generate_profiles(folder_path: Path, type_profiles: dict[str, list[str]]) -> dict[str, list[str]]:
    file_paths = [file_path for file_path in folder_path.iterdir() if file_path.is_file()]
    profiles: dict[str, list[str]] = {}
    for file_path in file_paths:
        file_name = file_path.name
        mime_type = mimetypes.guess_type(file_path)[0]
        if mime_type is None: raise Exception(f"Cannot guess mimetype for {file_path}")
        file_type = mime_type.split("/")[0]
        if file_type in type_profiles:
            profiles[file_name] = type_profiles[file_type]
    return profiles
