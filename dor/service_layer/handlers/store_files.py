from pathlib import Path
from dor.domain.events import PackageStored, PackageUnpacked
from dor.providers.package_resources_merger import PackageResourcesMerger
from dor.service_layer.unit_of_work import AbstractUnitOfWork
from dor.providers.descriptor_generator import DescriptorGenerator

def store_files(event: PackageUnpacked, uow: AbstractUnitOfWork, workspace_class: type) -> None:
    workspace = workspace_class(event.workspace_identifier, event.identifier)

    entries: list[Path] = []
    for resource in event.resources:
        entries.extend(resource.get_entries())

    bundle = workspace.get_bundle(entries)

    revision = uow.catalog.get(event.identifier)
    if revision is None: 
        uow.gateway.create_staged_object(id=event.identifier)

    uow.gateway.stage_object_files(
        id=event.identifier,
        source_bundle=bundle,
    )

    resources = event.resources
    if revision:
        print("-- ahoy revising!")
        merger = PackageResourcesMerger(current=revision.package_resources, incoming=resources)
        resources = merger.merge_changes()

    generator = DescriptorGenerator(
        package_path=workspace.object_data_directory(),
        resources=resources
    )
    generator.write_files()
    descriptor_bundle = workspace.get_bundle(generator.entries)
    uow.gateway.stage_object_files(
        id=event.identifier,
        source_bundle=descriptor_bundle,
    )

    uow.gateway.commit_object_changes(
        id=event.identifier,
        coordinator=event.version_info.coordinator,
        message=event.version_info.message,
    )

    version_log = uow.gateway.log(id=event.identifier)
    revision_number = version_log[0].version

    stored_event = PackageStored(
        identifier=event.identifier,
        workspace_identifier=event.workspace_identifier,
        tracking_identifier=event.tracking_identifier,
        package_identifier=event.package_identifier,
        resources=resources,
        update_flag=event.update_flag,
        revision_number=revision_number,
    )
    uow.add_event(stored_event)
