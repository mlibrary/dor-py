from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Body, Depends

from dor.entrypoints.api.dependencies import get_inbox_path
from dor.providers.package_generator import DepositGroup
from dor.providers.packages import create_package_from_metadata
from dor.queues import queues


packages_router = APIRouter(prefix="/packages")


@dataclass
class PackageResponse:
    identifier: str
    deposit_group_identifier: str


@packages_router.post("/")
async def create_package(
    deposit_group: Annotated[dict[str, str], Body(...)],
    package_metadata: Annotated[dict, Body(...)],
    inbox_path: Path=Depends(get_inbox_path)
) -> PackageResponse:
    deposit_group_ = DepositGroup(
        deposit_group["identifier"],
        datetime.fromisoformat(deposit_group["date"])
    )

    queues["package"].enqueue(
        create_package_from_metadata,
        deposit_group_,
        package_metadata,
        inbox_path
    )

    return PackageResponse(
        identifier=package_metadata["identifier"],
        deposit_group_identifier=deposit_group_.identifier
    )
