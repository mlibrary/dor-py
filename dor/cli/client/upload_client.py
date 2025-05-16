import copy
import json
import mimetypes
import httpx
import os
from typing import List, Optional, Any, Tuple


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
    file: List[str],
    folder: Optional[str] = None,
    name: Optional[str] = None,
    project_id: Optional[str] = None,
    commands: Optional[str] = None,  
    process_individually: bool = True,
) -> Any:
    """Upload fileset with dynamic profile-based commands."""
    upload_files = []
    try:
        # Determine file paths
        if folder:
            if not os.path.exists(folder) or not os.path.isdir(folder):
                raise UploadError(
                    f"Folder '{folder}' does not exist or is not a directory.", code=404
                )
            file_paths = [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if os.path.isfile(os.path.join(folder, f))
            ]
            if not file_paths:
                raise UploadError(f"No files found in folder '{folder}'.", code=404)
        elif file:
            file_paths = file
        else:
            raise UploadError("Either 'file' or 'folder' must be provided.", code=400)

        upload_files = prepare_files(file_paths)

        if commands:
            commands_ = {}
            for file_path in file_paths:
                commands_.update(generate_commands(commands, file_path))
        else:
            raise UploadError(
                "Profile must be provided", code=400
            )

        params = {
            "name": name,
            "project_id": project_id,
            "commands": json.dumps(commands_),  # Serialize commands to JSON
        }
        params = {k: v for k, v in params.items() if v is not None}

        # Process files individually or as a group
        if process_individually:
            return await upload_individual_files(client, base_url, upload_files, params)
        else:
            return await upload_grouped_files(client, base_url, upload_files, params)

    finally:
        # Ensure all file streams are closed
        for _, (_, upload_file_fh) in upload_files:
            upload_file_fh.close()


def prepare_files(file_paths: List[str]) -> List[Tuple[str, Tuple[str, Any]]]:
    upload_files = []
    for file_path in file_paths:
        if not os.path.exists(file_path):
            raise UploadError(f"File '{file_path}' does not exist.", code=404)
        upload_files.append(
            (
                "files",
                (
                    os.path.basename(file_path),
                    open(file_path, "rb"),
                ),
            )
        )
    return upload_files


def generate_commands(command: str, file_path: str) -> dict:

    mime_type, _ = mimetypes.guess_type(file_path)
    if not mime_type:
        raise ValueError(f"Could not determine MIME type for file: {file_path}")

    # Define operations based on MIME type
    mime_operations = {
        "text/plain": {
            "operation": "AppendUses",
            "args": {
                "target": {
                    "function": ["function:source"],
                    "format": "format:text-plain",
                },
                "uses": ["function:service"],
            },
        },
        "image/jpeg": {
            "operation": "CompressSourceImage",
            "args": {},
        },
        "image/jpg": {
            "operation": "CompressSourceImage",
            "args": {},
        },
        "image/jp2": {
            "operation": "CompressSourceImage",
            "args": {},
        },
        "image/tiff": {
            "operation": "CompressSourceImage",
            "args": {},
        },
    }

    if mime_type not in mime_operations:
        raise ValueError(f"Unsupported MIME type: {mime_type}")

    operation = mime_operations[mime_type]

    return {os.path.basename(file_path): operation}


async def upload_individual_files(
    client: httpx.AsyncClient,
    base_url: str,
    upload_files: List[Tuple[str, Tuple[str, Any]]],
    params: dict,
) -> List[Any]:
    """Upload files individually."""
    response_bodies = []

    for upload_file in upload_files:

        response = await client.post(
            f"{base_url}/api/v1/filesets", files=[upload_file], data=params
        )
        response.raise_for_status()
        response_bodies.append(response.json())

    return response_bodies


async def upload_grouped_files(
    client: httpx.AsyncClient,
    base_url: str,
    upload_files: List[Tuple[str, Tuple[str, Any]]],
    params: dict,
) -> Any:
    """Upload files as a group."""
    response = await client.post(
        f"{base_url}/api/v1/filesets", files=upload_files, data=params
    )
    response.raise_for_status()
    return response.json()
