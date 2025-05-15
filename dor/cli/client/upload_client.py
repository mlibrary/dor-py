import copy
import json
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
    folder: str = None,
    name: str = None,
    project_id: str = None,
    commands: str = None,
    process_individually: bool = True,
) -> Any:
    upload_files = []
    try:
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

        params = {
            "name": name,
            "project_id": project_id,
            "commands": commands,
        }
        params = {k: v for k, v in params.items() if v is not None}

        # Process files individually or as a group
        if process_individually:
            return await upload_individual_files(client, base_url, upload_files, params)
        else:
            return await upload_grouped_files(client, base_url, upload_files, params)

    finally:
        # Ensure all file streams are closed
        for _, (_, upload_file) in upload_files:
            upload_file.close()

def prepare_files(file_paths: List[str]) -> List[Tuple[str, Tuple[str, Any]]]:
    upload_files = []
    for file_path in file_paths:
        if not os.path.exists(file_path):
            raise UploadError(f"File '{file_path}' does not exist.", code=404)
        upload_files.append(
            (
                "file",
                (
                    os.path.basename(file_path),  
                    open(file_path, "rb"),  
                ),
            )
        )
    return upload_files

async def upload_individual_files(
    client: httpx.AsyncClient,
    base_url: str,
    upload_files: List[Tuple[str, Tuple[str, Any]]],
    params: dict,
) -> List[Any]:
    response_bodies = []

    for upload_file in upload_files:
        params_data = copy.deepcopy(params)
        print("upload file:",upload_file)
        # file_name = upload_file[1][0]
        _, (file_basename, _) = upload_file
        file_name = file_basename
        
        params_data["commands"] = params_data["commands"].format(file_path=file_name)
        print(params_data)
        response = await client.post(
            f"{base_url}/api/v1/filesets", files=[upload_file], data=params_data
        )
        
        print ("response:",response)
        response.raise_for_status()
        response_bodies.append(response.json())

    return response_bodies


async def upload_grouped_files(
    client: httpx.AsyncClient,
    base_url: str,
    upload_files: List[Tuple[str, Tuple[str, Any]]],
    params: dict,
) -> Any:
    response = await client.post(
        f"{base_url}/api/v1/filesets", files=upload_files, data=params
    )
    response.raise_for_status()
    return response.json()
