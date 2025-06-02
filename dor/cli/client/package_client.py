import json
import uuid
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Generator, Self

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
