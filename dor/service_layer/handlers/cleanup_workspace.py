import json
from datetime import datetime, UTC
from pathlib import Path

from dor.domain.events import WorkspaceCleaned
from dor.domain.models import Revision
from dor.providers.file_provider import FileProvider
from dor.service_layer.unit_of_work import AbstractUnitOfWork

def cleanup_workspace(event: WorkspaceCleaned, uow: AbstractUnitOfWork, workspace_class: type, file_provider: FileProvider) -> None:
    workspace = workspace_class(event.workspace_identifier)

    file_provider.delete_dir_and_contents(workspace.package_directory())

    uow.add_event(WorkspaceCleaned(
        identifier=event.identifier,
        package_identifier=event.package_identifier,
        tracking_identifier=event.tracking_identifier,
        update_flag=event.update_flag,))
    