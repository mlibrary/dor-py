from datetime import datetime
from dataclasses import dataclass
from typing import Annotated

from fastapi import APIRouter, Body

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
    package_metadata: Annotated[dict, Body(...)],
    deposit_group: Annotated[dict[str, str], Body(...)]
) -> PackageResponse:
    deposit_group_ = DepositGroup(
        deposit_group["identifier"],
        datetime.fromisoformat(deposit_group["date"])
    )

    queues["package"].enqueue(
        create_package_from_metadata,
        deposit_group_,
        package_metadata
    )

    return PackageResponse(
        identifier=package_metadata["identifier"],
        deposit_group_identifier=deposit_group_.identifier
    )
