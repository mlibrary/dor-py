import asyncio
import json
import uuid
from dataclasses import dataclass
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

import httpx


@dataclass
class DepositGroup:
    identifier: str
    date: datetime


def create_deposit_group() -> DepositGroup:
    return DepositGroup(
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


async def upload_package(
    client: httpx.AsyncClient,
    deposit_group: DepositGroup,
    package_metadata: dict[str, Any]
) -> dict[str, Any]:
    body = {
        "deposit_group": {
            "identifier": deposit_group.identifier,
            "date": deposit_group.date.isoformat()
        },
        "package_metadata": package_metadata
    }
    response = await client.post("/packages/", json=body)
    response.raise_for_status()
    return response.json()


async def upload_packages(
    client: httpx.AsyncClient,
    deposit_group: DepositGroup,
    package_metadatas: list[dict[str, Any]]
) -> list[dict[str, Any] | BaseException]:
    tasks = []
    for package_metadata in package_metadatas:
        tasks.append(upload_package(
            client=client,
            deposit_group=deposit_group,
            package_metadata=package_metadata
        ))
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
