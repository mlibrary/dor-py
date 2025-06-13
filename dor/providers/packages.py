from typing import Any
from datetime import datetime, UTC
from pathlib import Path

from dor.adapters import eventpublisher
from dor.domain.events import PackageGenerated
from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.repository_client import FakeRepositoryClient
from dor.providers.package_generator import (DepositGroup, PackageGenerator)
from dor.queues import queues


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

    package_result = PackageGenerator(
        file_provider=FilesystemFileProvider(),
        repository_client=FakeRepositoryClient(),
        metadata=package_metadata,
        deposit_group=deposit_group,
        output_path=inbox_path,
        file_sets_path=pending_path,
        timestamp=datetime.now(tz=UTC)
    ).generate()

    event = PackageGenerated(
        package_identifier=package_result.package_identifier,
        # FIXME: establish real tracking (submission) identifier
        # TODO: decide whether this would be assigned now or at start of ingest
        tracking_identifier="not-yet-figured-out"
    )
    eventpublisher.publish(event)
