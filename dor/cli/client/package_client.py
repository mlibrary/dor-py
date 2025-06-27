import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator

import httpx

from dor.providers.models import DepositGroup


def get_package_metadata_records(packet_path: Path) -> Generator[dict[str, Any], None, None]:
    with open(packet_path, "r") as file:
        for line in file:
            if not line.strip(): continue
            metadata = json.loads(line)
            yield metadata


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


@dataclass
class PackagesUploadResult:
    response_datas: list[dict[str, Any]]
    exceptions: list[Exception]


async def upload_packages(
    packet_path: Path,
    httpx_client: httpx.AsyncClient,
    deposit_group: DepositGroup
):
    response_datas = []
    exceptions = []

    async with httpx_client:
        for package_metadata in get_package_metadata_records(packet_path):
            try:
                result = await upload_package(
                    client=httpx_client,
                    deposit_group=deposit_group,
                    package_metadata=package_metadata
                )
                response_datas.append(result)
            except Exception as exception:
                exceptions.append(exception)

    return PackagesUploadResult(
        response_datas=response_datas,
        exceptions=exceptions
    )
