from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Body

from dor.providers.package_generator import DepositGroup
from dor.providers.packages import create_package_from_metadata
from dor.queues import queues


packages_router = APIRouter(prefix="/packages")


@packages_router.post("/")
async def create_package(
    package_metadata: Annotated[dict, Body(...)],
    deposit_group: Annotated[dict[str, str], Body(...)]
):
    deposit_group_ = DepositGroup(
        deposit_group["identifier"],
        datetime.fromisoformat(deposit_group["date"])
    )

    queues["package"].enqueue(
        create_package_from_metadata,
        deposit_group_,
        package_metadata
    )

    return {}
