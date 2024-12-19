from dor.adapters.bag_adapter import ValidationError
from dor.domain.events import PackageNotVerified, PackageReceived, PackageVerified
from dor.service_layer.unit_of_work import UnitOfWork


def verify_package(
    event: PackageReceived, uow: UnitOfWork, bag_adapter_class: type, workspace_class: type
) -> None:
    workspace = workspace_class(event.workspace_identifier)

    bag_adapter = bag_adapter_class(workspace.package_directory())

    try:
        bag_adapter.validate()
        uow.add_event(PackageVerified(
            package_identifier=event.package_identifier,
            tracking_identifier=event.tracking_identifier,
            workspace_identifier=workspace.identifier,
        ))
    except ValidationError as e:
        uow.add_event(PackageNotVerified(
            package_identifier=event.package_identifier,
            tracking_identifier=event.tracking_identifier,
            message=e.message
        ))
