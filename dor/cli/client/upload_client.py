import httpx
import typer
import os
from typing import List, Optional, Any

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
    collection: str = None,
    profile: str = None,
) -> Any:
    upload_files = []

    try:
        if folder:
            if not os.path.exists(folder) or not os.path.isdir(folder):
                raise UploadError(
                    f"Folder '{folder}' does not exist or is not a directory.", code=404
                )

            files = [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if os.path.isfile(os.path.join(folder, f))
            ]
            if not files:
                raise UploadError(f"No files found in folder '{folder}'.", code=404)

            for file_path in files:
                upload_files.append(
                    (
                        "files",
                        (
                            os.path.basename(file_path),
                            open(file_path, "rb"),
                        ),
                    )
                )

        elif file:
            for file_path in file:
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

        else:
            raise UploadError("Either 'file' or 'folder' must be provided.", code=400)

        params = {
            "name": name,
            "collection": collection,
            "profile": profile,
        }
        params = {k: v for k, v in params.items() if v is not None}

        # Perform the HTTP request
        response = await client.post(
            f"{base_url}/api/v1/filesets", files=upload_files, data=params
        )

        response.raise_for_status()
        return response.json()

    finally:
        # Ensure all file streams are closed
        for _, (_, file) in upload_files:
            file.close()
