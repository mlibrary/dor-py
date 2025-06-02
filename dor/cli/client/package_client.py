import asyncio
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Self

import httpx


@dataclass
class DepositGroup:
    identifier: str
    date: datetime

    @classmethod
    def generate(cls) -> Self:
        return cls(
            identifier=str(uuid.uuid4()),
            date=datetime.now(tz=UTC)
        )


def get_package_metadatas(packet_path: Path) -> list[dict[str, Any]]:
    package_metadatas = []
    with open(packet_path, "r") as file:
        for line in file:
            if not line.strip(): continue
            metadata = json.loads(line)
            package_metadatas.append(metadata)
    return package_metadatas


class PackageUploadError(Exception):

    def __init__(self, message: str, package_identifier: str):
        super().__init__(message)
        self.message = message
        self.package_identifier = package_identifier


async def upload_package(
    client: httpx.AsyncClient,
    deposit_group: DepositGroup,
    package_metadata: dict[str, Any]
) -> dict[str, Any]:
    package_identifier = package_metadata["identifier"]
    body = {
        "deposit_group": {
            "identifier": deposit_group.identifier,
            "date": deposit_group.date.isoformat()
        },
        "package_metadata": package_metadata
    }

    try:
        response = await client.post("/packages/", json=body)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as error:
        raise PackageUploadError(
            message=f"HTTP error occurred: {error.response.status_code} - {error.response.text}",
            package_identifier=package_identifier
        ) from error
    except httpx.HTTPError as error:
        raise PackageUploadError(
            message=f"An error occurred while making a request: {error}",
            package_identifier=package_identifier
        ) from error


async def upload_package_with_limit(
    sempahore: asyncio.Semaphore,
    client: httpx.AsyncClient,
    deposit_group: DepositGroup,
    package_metadata: dict[str, Any]
) -> dict[str, Any]:
    async with sempahore:
        result = await upload_package(
            client=client,
            deposit_group=deposit_group,
            package_metadata=package_metadata
        )
    return result


@dataclass
class UploadResult:
    response_datas: list[dict[str, Any]]
    exceptions: list[BaseException]


async def upload_packages(
    client: httpx.AsyncClient,
    deposit_group: DepositGroup,
    package_metadatas: list[dict[str, Any]]
) -> UploadResult:
    semaphore = asyncio.Semaphore(10)

    async with client:
        tasks = []
        for package_metadata in package_metadatas:
            tasks.append(upload_package_with_limit(
                sempahore=semaphore,
                client=client,
                deposit_group=deposit_group,
                package_metadata=package_metadata
            ))
        results = await asyncio.gather(*tasks, return_exceptions=True)

    response_datas = []
    exceptions = []
    for result in results:
        if isinstance(result, BaseException):
            exceptions.append(result)
        else:
            response_datas.append(result)

    return UploadResult(
        response_datas=response_datas,
        exceptions=exceptions
    )
