from typing import Any
# from datetime import datetime, UTC
# from pathlib import Path

# from dor.config import config
# from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.package_generator import (DepositGroup, ) # PackageGenerator
# from dor.providers.repository_client import FakeRepositoryClient


def create_package_from_metadata(deposit_group: DepositGroup, package_metadata: dict[str, Any]):
    print(deposit_group)
    print(package_metadata)

    # PackageGenerator(
    #     file_provider=FilesystemFileProvider(),
    #     repository_client=FakeRepositoryClient(),
    #     metadata=package_metadata,
    #     deposit_group=deposit_group,
    #     output_path=Path("to/be/determined"),
    #     file_sets_path=Path(config.filesets_path),
    #     timestamp=datetime.now(tz=UTC)
    # ).generate()
