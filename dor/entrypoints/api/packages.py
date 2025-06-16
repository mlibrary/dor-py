from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends

from dor.adapters import eventpublisher
from dor.domain import commands
from dor.entrypoints.api.dependencies import get_inbox_path, get_pending_path


packages_router = APIRouter(prefix="/packages")


@dataclass
class PackageResponse:
    identifier: str
    deposit_group_identifier: str


@packages_router.post("/")
async def create_package(
    deposit_group: Annotated[dict[str, str], Body(...)],
    package_metadata: Annotated[dict[str, Any], Body(...)],
    inbox_path: Path=Depends(get_inbox_path),
    pending_path: Path=Depends(get_pending_path),
) -> PackageResponse:
    eventpublisher.publish(commands.CreatePackage(
        deposit_group["identifier"],
        deposit_group["date"],
        package_metadata,
    ))

    return PackageResponse(
        identifier=package_metadata["identifier"],
        deposit_group_identifier=deposit_group["identifier"]
    )
