from typing import Any
# from datetime import datetime, UTC
from pathlib import Path

# from dor.config import config
from dor.providers.automation import run_automation
from dor.queues import queues
# from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.package_generator import (DepositGroup, ) # PackageGenerator
# from dor.providers.repository_client import FakeRepositoryClient


def create_package_from_metadata(
    deposit_group: DepositGroup,
    package_metadata: dict[str, Any],
    inbox_path: Path,
    pending_path: Path
):
    print(deposit_group)
    print(package_metadata)
    print(inbox_path)
    print(pending_path)

    identifier = package_metadata["identifier"]

    # TODO: Uncomment once PackageGenerator is updated to handle fileset paths
    # PackageGenerator(
    #     file_provider=FilesystemFileProvider(),
    #     repository_client=FakeRepositoryClient(),
    #     metadata=package_metadata,
    #     deposit_group=deposit_group,
    #     output_path=inbox_path,
    #     file_sets_path=pending_path,
    #     timestamp=datetime.now(tz=UTC)
    # ).generate()

    queues["automation"].enqueue(run_automation, "package.success", package_identifier=identifier)
