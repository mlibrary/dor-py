from pathlib import Path
from dor.domain.events import PackageStored, PackageUnpacked
from dor.service_layer.unit_of_work import UnitOfWork


def store_files(event: PackageUnpacked, uow: UnitOfWork, workspace_class: type) -> None:
    workspace = workspace_class(event.workspace_identifier, event.identifier)

    entries: list[Path] = []
    for resource in event.resources:
        entries.extend(resource.get_entries())

    bundle = workspace.get_bundle(entries)

    uow.gateway.create_staged_object(id=event.identifier)
    uow.gateway.stage_object_files(
        id=event.identifier,
        source_bundle=bundle,
    )
    uow.gateway.commit_object_changes(
        id=event.identifier,
        coordinator=event.version_info.coordinator,
        message=event.version_info.message,
    )

    stored_event = PackageStored(
        identifier=event.identifier, tracking_identifier=event.tracking_identifier
    )
    uow.add_event(stored_event)
