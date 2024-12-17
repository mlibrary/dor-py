

from dor.domain.events import PackageReceived, PackageVerified
from dor.service_layer.unit_of_work import UnitOfWork

def verify_package(event: PackageReceived, uow: UnitOfWork, bag_reader_class: type, workspace_class: type) -> None:
    workspace = workspace_class(event.workspace_identifier)

    bag_reader = bag_reader_class(workspace.package_directory)

    is_valid = bag_reader.is_valid()

    if is_valid:
        uow.add_event(PackageVerified(
            package_identifier=event.package_identifier,
            tracking_identifier=event.tracking_identifier,
            workspace_identifier=workspace.identifier,
        ))
    else:
        raise Exception()