import json
from datetime import datetime, UTC
from pathlib import Path

from dor.domain.events import PackageStored, RevisionCataloged
from dor.domain.models import Revision
from dor.service_layer.unit_of_work import AbstractUnitOfWork

def catalog_revision(event: PackageStored, uow: AbstractUnitOfWork) -> None:
    root_resource = [resource for resource in event.resources if resource.type == 'Monograph'][0]
    common_metadata_file = [
        metadata_file for metadata_file in root_resource.metadata_files if "common" in metadata_file.ref.locref
    ][0]
    common_metadata_file_path = Path(common_metadata_file.ref.locref)
    object_files = uow.gateway.get_object_files(event.identifier)
    matching_object_file = [
        object_file for object_file in object_files if common_metadata_file_path == object_file.logical_path
    ][0]
    literal_common_metadata_path = matching_object_file.literal_path
    common_metadata = json.loads(literal_common_metadata_path.read_text())

    revision = Revision(
        identifier=event.identifier,
        alternate_identifiers=[root_resource.alternate_identifier.id],
        revision_number=1,
        created_at=datetime.now(tz=UTC),
        common_metadata=common_metadata,
        package_resources=event.resources
    )
    with uow:
        uow.catalog.add(revision)
        uow.commit()

    uow.add_event(RevisionCataloged(
        identifier=event.identifier,
        workspace_identifier=event.workspace_identifier,
        tracking_identifier=event.tracking_identifier,
        package_identifier=event.package_identifier,
        update_flag=event.update_flag,
    ))
    