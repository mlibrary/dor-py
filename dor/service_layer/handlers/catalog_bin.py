import json
from pathlib import Path

from dor.domain.events import PackageStored, BinCataloged
from dor.domain.models import Bin
from dor.service_layer.unit_of_work import AbstractUnitOfWork

def catalog_bin(event: PackageStored, uow: AbstractUnitOfWork) -> None:
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

    bin = Bin(
        identifier=event.identifier,
        alternate_identifiers=[root_resource.alternate_identifier.id],
        common_metadata=common_metadata,
        package_resources=event.resources
    )
    with uow:
        uow.catalog.add(bin)
        uow.commit()

    uow.add_event(BinCataloged(identifier=event.identifier, tracking_identifier=event.tracking_identifier))
    